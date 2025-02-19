#include <Wire.h>
#include <Adafruit_ADS1X15.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <freertos/FreeRTOS.h>
#include <freertos/queue.h>

// Configuración de la red WiFi
const char* ssid = "Repeater_oficina";         // Reemplaza con tu red WiFi
const char* password = "Cuenta_Wifi@Pueblo";   // Reemplaza con tu contraseña

// Configuración del broker MQTT
const char* mqtt_server = "138.100.69.52";     //  EL IP termina en RPi1:.38  RPi2= .52

WiFiClient espClient;
PubSubClient client(espClient);

Adafruit_ADS1115 ads1;
Adafruit_ADS1115 ads2;

QueueHandle_t dataQueue;

struct SensorData {
    int16_t canal1;
    int16_t canal2;
    int16_t canal3;
    int16_t canal4;
};

void conectarWiFi() {
    Serial.print("[INFO] Conectando a WiFi: ");
    Serial.println(ssid);

    WiFi.begin(ssid, password);
    int intentos = 0;
    while (WiFi.status() != WL_CONNECTED && intentos < 20) { 
        delay(1000);
        Serial.print(".");
        intentos++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n[INFO] ¡Conectado a WiFi con éxito!");
        Serial.print("[INFO] Dirección IP: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("\n[ERROR] No se pudo conectar a WiFi. Verifica SSID/contraseña.");
        while (true); // Detiene el código si no hay conexión WiFi
    }
}

void conectarMQTT() {
    client.setServer(mqtt_server, 1883);
    while (!client.connected()) {
        Serial.print("[INFO] Conectando a MQTT...");
        if (client.connect("ArduinoNanoESP32")) {
            Serial.println(" ¡Conectado a MQTT!");
        } else {
            Serial.print(" Fallo, código: ");
            Serial.print(client.state());
            Serial.println(" Intentando de nuevo...");
            delay(2000);
        }
    }
}

void setup() {
    Serial.begin(115200);
    Serial.println("[INFO] Iniciando Arduino Nano ESP32...");

    conectarWiFi();
    conectarMQTT();
    
    // Configuración de los ADS1115
    Wire.begin(21, 22);
    Wire.setClock(400000);

    Wire1.begin(4, 5);
    Wire1.setClock(400000);

    if (!ads1.begin(0x48, &Wire)) {
        Serial.println("[ERROR] No se pudo inicializar ADS1115 en 0x48");
        while (1);
    }
    if (!ads2.begin(0x49, &Wire1)) {
        Serial.println("[ERROR] No se pudo inicializar ADS1115 en 0x49");
        while (1);
    }

    ads1.setGain(GAIN_ONE);
    ads2.setGain(GAIN_ONE);
    ads1.setDataRate(RATE_ADS1115_860SPS);
    ads2.setDataRate(RATE_ADS1115_860SPS);

    Serial.println("[INFO] ¡Configuración de sensores completada!");

    // Crear la cola para almacenar los datos de los sensores
    dataQueue = xQueueCreate(20, sizeof(SensorData));  // Aumentar el tamaño de la cola

    // Crear tareas en los núcleos
    xTaskCreatePinnedToCore(
        leerSensores,   // Función de la tarea
        "LeerSensores", // Nombre de la tarea
        10000,          // Tamaño de la pila
        NULL,           // Parámetro de entrada
        2,              // Prioridad de la tarea (aumentada)
        NULL,           // Manejador de la tarea
        0);             // Núcleo 0

    xTaskCreatePinnedToCore(
        enviarMQTT,     // Función de la tarea
        "EnviarMQTT",   // Nombre de la tarea
        10000,          // Tamaño de la pila
        NULL,           // Parámetro de entrada
        1,              // Prioridad de la tarea
        NULL,           // Manejador de la tarea
        1);             // Núcleo 1
}

void leerSensores(void * parameter) {
    unsigned long lastReadingTime = 0;
    unsigned long readingInterval = 1000000 / 860;

    while (true) {
        if (micros() - lastReadingTime >= readingInterval) {
            SensorData data;
            data.canal1 = ads1.readADC_SingleEnded(0);
            data.canal2 = ads1.readADC_SingleEnded(1);
            data.canal3 = ads2.readADC_SingleEnded(0);
            data.canal4 = ads2.readADC_SingleEnded(1);

            // Enviar los datos a la cola
            xQueueSend(dataQueue, &data, portMAX_DELAY);

            lastReadingTime = micros();
        }
    }
}

void enviarMQTT(void * parameter) {
    while (true) {
        if (!client.connected()) {
            conectarMQTT();
        }

        SensorData data;
        if (xQueueReceive(dataQueue, &data, portMAX_DELAY) == pdPASS) {
            char msg[100];
            snprintf(msg, sizeof(msg), "{\"C1\":%d,\"C2\":%d,\"C3\":%d,\"C4\":%d}",
                     data.canal1, data.canal2, data.canal3, data.canal4);

            client.publish("sensores/datos", msg);
        }

        client.loop();
        delay(1);  // Reducir el retardo para mejorar la velocidad
    }
}

void loop() {
    // El loop principal queda vacío ya que las tareas se manejan en los núcleos
}

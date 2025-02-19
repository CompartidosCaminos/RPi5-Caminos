import os
import csv
import datetime
import glob
import matplotlib.pyplot as plt

# Directorios de trabajo
CSV_INPUT_DIR = "RAW"
CSV_OUTPUT_DIR = "/home/caminos/ADS/RESISTENCIAS"

# Asegurar que la carpeta de salida existe
if not os.path.exists(CSV_OUTPUT_DIR):
    os.makedirs(CSV_OUTPUT_DIR)

def calcular_resistencias(csv_filename):
    output_filename = generar_nombre_archivo()
    input_path = os.path.join(CSV_INPUT_DIR, csv_filename)
    output_path = os.path.join(CSV_OUTPUT_DIR, output_filename)

    try:
        with open(input_path, "r") as infile, open(output_path, "w", newline='') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            # Leer encabezados y escribir nuevos encabezados
            headers = next(reader)
            writer.writerow(["R1 (C2-C1)", "R2 (C3-C2)", "R3 (C4-C3)", "R4 (C3-C1)", "R5 (C4-C1)", "R6 (C4-C2)"])

            row_count = 0  # Contador de l�neas procesadas

            for row in reader:
                try:
                    c1, c2, c3, c4 = map(float, row)
                    if c1 == 0:  # Evitar divisi�n por cero
                        continue
                    i1 = c1 / 10  # Corriente en la resistencia de 10O
                    r1 = (c2 - c1) / i1
                    r2 = (c3 - c2) / i1
                    r3 = (c4 - c3) / i1
                    r4 = (c3 - c1) / i1
                    r5 = (c4 - c1) / i1
                    r6 = (c4 - c2) / i1
                    writer.writerow([r1, r2, r3, r4, r5, r6])
                    row_count += 1
                except ValueError:
                    continue  # Omitir l�neas inv�lidas     # A�adir una l�nea al final con el total de l�neas escritas
            writer.writerow(["Total l�neas:", row_count])
        print(f"[INFO] Archivo generado: {output_path}")
        return output_path  # Devolvemos la ruta del archivo generado
    except Exception as e:
        print(f"[ERROR] No se pudo procesar {csv_filename}: {e}")
        return None

def generar_nombre_archivo():
    fecha = datetime.datetime.now().strftime("%d%m%Y")
    archivos_existentes = glob.glob(os.path.join(CSV_OUTPUT_DIR, f"{fecha}_Ensayo_*.csv"))
    numero = len(archivos_existentes) + 1
    return f"{fecha}_Ensayo_{numero}.csv"

# Funci�n para obtener el CSV m�s reciente de la carpeta de entrada
def obtener_csv_mas_reciente():
    archivos = sorted(glob.glob(os.path.join(CSV_INPUT_DIR, "*.csv")), key=os.path.getmtime, reverse=True)
    return archivos[0] if archivos else None

# Funci�n para graficar los valores de cada resistencia calculada
def graficar_resistencias(csv_file):
    indices = []
    r1_values = []
    r2_values = []
    r3_values = []
    r4_values = []
    r5_values = []
    r6_values = []

    try:
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            header = next(reader)  # Se asume que la primera l�nea son los encabezados

            for i, row in enumerate(reader, start=1):
                # Si se encuentra la l�nea final con el total de l�neas, se interrumpe la lectura
                if row and row[0].strip().lower() == "total l�neas:":
                    break
                try:
                    # Convertir cada valor a float
                    val1, val2, val3, val4, val5, val6 = map(float, row)
                    indices.append(i)
                    r1_values.append(val1)
                    r2_values.append(val2)
                    r3_values.append(val3)
                    r4_values.append(val4)
                    r5_values.append(val5)
                    r6_values.append(val6)
                except ValueError:
                    continue  # Omitir filas inv�lidas
    except Exception as e:
        print(f"[ERROR] No se pudo leer el archivo {csv_file}: {e}")
        return # Configuraci�n y creaci�n del gr�fico
    plt.figure(figsize=(10, 6))
    plt.plot(indices, r1_values, label='R1 (C2-C1)')
    plt.plot(indices, r2_values, label='R2 (C3-C2)')
    plt.plot(indices, r3_values, label='R3 (C4-C3)')
    plt.plot(indices, r4_values, label='R4 (C3-C1)')
    plt.plot(indices, r5_values, label='R5 (C4-C1)')
    plt.plot(indices, r6_values, label='R6 (C4-C2)')

    plt.xlabel('N�mero de Muestra')
    plt.ylabel('Valor de la Resistencia')
    plt.title('Gr�fico de Resistencias Calculadas')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# --- Bloque Principal ---
if __name__ == "__main__":
    csv_reciente = obtener_csv_mas_reciente()
    if csv_reciente:
        # Calculamos las resistencias a partir del CSV m�s reciente y obtenemos el archivo generado
        archivo_generado = calcular_resistencias(os.path.basename(csv_reciente))
        # Si se gener� correctamente el archivo, lo graficamos
        if archivo_generado:
            graficar_resistencias(archivo_generado)
    else:
        print("[WARNING] No hay archivos CSV en RAW para procesar.")

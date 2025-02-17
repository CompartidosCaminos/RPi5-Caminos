import pandas as pd
import sys
import os

# Configuraci�n del ADS1115
ADS_GAIN = 4.096  # Voltaje m�ximo en el ADS1115 (puede ser 6.144, 4.096, etc.)
RESOLUTION = 32768  # Resoluci�n del ADS1115 (16 bits)

# Verifica si se pas� el archivo como argumento
if len(sys.argv) < 2:
    print("[ERROR] No se proporcion� un archivo para procesar.")
    sys.exit(1)

filename = sys.argv[1]

if not os.path.exists(filename):
    print(f"[ERROR] Archivo {filename} no encontrado.")
    sys.exit(1)

try:
    # Cargar los datos RAW
    df = pd.read_csv(filename)

    # Verificar si la columna 'raw' existe
    if 'raw' not in df.columns:
        print("[ERROR] El archivo no contiene la columna 'raw'.")
        sys.exit(1)

    # Convertir a voltaje
    df["voltaje"] = (df["raw"] / RESOLUTION) * ADS_GAIN

    # Guardar el archivo procesado
    processed_filename = filename.replace("datos_", "procesado_")
    df.to_csv(processed_filename, index=False)
    print(f"[INFO] Archivo procesado guardado en: {processed_filename}")

except Exception as e:
    print(f"[ERROR] No se pudo procesar el archivo: {e}")

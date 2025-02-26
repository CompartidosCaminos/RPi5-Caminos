import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.title("Visualizador de Resistencias y C�lculo de Velocidad (Pico a Pico)")
st.markdown("""
Esta aplicaci�n permite cargar el archivo generado por `resistencias.py` y:
- Visualizar las curvas (normalizadas) en funci�n del tiempo (se asume una adquisici�n total de 5 s).
- Seleccionar individualmente qu� curvas mostrar mediante checkboxes.
- Calcular la velocidad pico a pico entre:
  - **R1 (C2-C1)** y **R2 (C3-C2)** (5 cm)
  - **R2 (C3-C2)** y **R3 (C4-C3)** (5 cm)
  - **R1 (C2-C1)** y **R3 (C4-C3)** (10 cm)
La velocidad se calcula como:
\[
\text{Velocidad (cm/s)} = \frac{\text{Distancia (cm)}}{\Delta t \, (\text{s})}
\]
y se convierte a km/h (1 cm/s = 0.036 km/h).
""")

# Subir archivo CSV
uploaded_file = st.file_uploader("Sube el archivo CSV generado", type=["csv"])

if uploaded_file is not None:
    # Cargar datos y mostrar tabla
    data = pd.read_csv(uploaded_file)
    st.write("Datos cargados:")
    st.dataframe(data)

    # Eliminar la �ltima fila si contiene "Total l�neas:"
    if "Total l�neas:" in data.iloc[-1].astype(str).values:
        data = data.iloc[:-1]

    # Definir los canales para el c�lculo de velocidades
    canales_calculo = ["R1 (C2-C1)", "R2 (C3-C2)", "R3 (C4-C3)"]

    # Definir distancias para cada par de medici�n (cm)
    valid_velocity_pairs = {
        ("R1 (C2-C1)", "R2 (C3-C2)"): 5,
        ("R2 (C3-C2)", "R3 (C4-C3)"): 5,
        ("R1 (C2-C1)", "R3 (C4-C3)"): 10,
    }

    # Crear eje de tiempo (se asume adquisici�n total de 5 s)
    total_time = 5.0  # segundos
    num_samples = len(data)
    dt = total_time / num_samples
    time_axis = np.arange(num_samples) * dt

  # Permitir al usuario seleccionar qu� curvas visualizar (checkbox para cada columna)
    st.markdown("### Selecci�n de curvas para visualizar")
    canales_visualizar = []
    for canal in data.columns:
        if st.checkbox(canal, value=True, key=f"chk_{canal}"):
            canales_visualizar.append(canal)

    # Gr�fica: se plotean las curvas seleccionadas, normalizando cada una (restando el primer valor)
    fig, ax = plt.subplots(figsize=(10, 6))
    # Tambi�n se calcular�n los tiempos pico para los canales de velocidad (R1, R2 y R3)
    peak_times = {}

    for canal in canales_visualizar:
        serie = data[canal].astype(float)
        serie_norm = serie - serie.iloc[0]
        ax.plot(time_axis, serie_norm, label=canal)
        # Si el canal est� entre los usados para velocidades, se calcula su pico
        if canal in canales_calculo:
            peak_index = serie_norm.idxmax()
            t_peak = time_axis[peak_index]
            peak_times[canal] = t_peak
            # Marcar el pico en el gr�fico
            ax.axvline(x=t_peak, linestyle='--', color='gray', alpha=0.5)
            ax.text(t_peak, np.max(serie_norm), f"{t_peak:.2f}s", rotation=90,
                    verticalalignment='bottom', fontsize=8)

    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Valor (normalizado)")
    ax.set_title("Curvas de Resistencias")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    st.markdown("### C�lculo de Velocidad (Pico a Pico)")
    st.markdown("""
Se calcular� la velocidad para cada par usando la diferencia en tiempo entre los picos:
- **Entre R1 y R2:** (5 cm)
- **Entre R2 y R3:** (5 cm)
- **Entre R1 y R3:** (10 cm)
    """)

    for (ch1, ch2), distancia in valid_velocity_pairs.items():
        if ch1 in peak_times and ch2 in peak_times:
            # Calcular diferencia absoluta de tiempo entre picos
            delta_t = abs(peak_times[ch2] - peak_times[ch1])
            if delta_t > 0:
                velocidad_cms = distancia / delta_t
                velocidad_kmh = velocidad_cms * 0.036
                st.write(f"**Entre {ch1} y {ch2}:** ?t = {delta_t:.3f} s | Distancia = {distancia} cm | "
                         f"Velocidad = {velocidad_cms:.2f} cm/s ({velocidad_kmh:.2f} km/h)")
            else:
                st.write(f"**Entre {ch1} y {ch2}:** ?t = 0 s, no se puede calcular la velocidad")
        else:
            st.write(f"**Entre {ch1} y {ch2}:** No se detectaron picos para ambos canales.")
else:
    st.info("Sube un archivo CSV para comenzar.")

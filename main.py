# --------------------------------------------
# main.py
# Script principal para simular y analizar el comportamiento de un parlante en aire libre.
# --------------------------------------------

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

# --------------------------------------------
# Importar librerías necesarias
# --------------------------------------------

import numpy as np                                                          # Para operaciones matemáticas y manejo de arrays
import matplotlib                                                           # Para graficar resultados
matplotlib.use("TkAgg")                                                     # Fuerza el uso del backend TkAgg para mostrar gráficos en ventana
import matplotlib.pyplot as plt                                             # Para crear gráficos y visualizaciones
import matplotlib.ticker as ticker                                          # Para formatear ejes en gráficos
from matplotlib.ticker import LogLocator, FixedLocator, ScalarFormatter     # Para formatear ejes logarítmicos y escalares
import mplcursors                                                           # Para agregar cursores interactivos a los gráficos

from core.driver import Driver                                              # Importa la clase Driver definida en core/driver.py

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

# --------------------------------------------
# Definir parámetros del altavoz
# --------------------------------------------

params = {
    "Fs": 40,                                   # Frecuencia de resonancia [Hz]
    "Mms": 0.025,                               # Masa móvil aproximada [kg]
    "Vas": 50,                                  # Volumen de aire equivalente [litros]
    "Qts": 0.35,                                # Factor de calidad total
    "Qes": 0.4,                                 # Factor de calidad eléctrico
    "Re": 6.0,                                  # Resistencia DC de la bobina [Ohm]
    "Bl": 7.5,                                  # Producto flujo-Bobina [N/A]
    "Sd": 0.02,                                 # Área efectiva del diafragma [m²]
    "Le": 0.0005                                # Inductancia de la bobina [Henrios]
}

my_driver = Driver(params)                      # Crea una instancia del driver con los parámetros definidos

# # --------------------------------------------
# # Mostrar parámetros derivados en consola
# # --------------------------------------------

# print(f"Mms: {my_driver.Mms:.4f} kg")                               # Masa móvil del diafragma
# print(f"Cms: {my_driver.Cms:.6f} m/N")                              # Complianza mecánica
# print(f"Rms: {my_driver.Rms:.4f} kg/s")                             # Resistencia mecánica
# print(f"Qms: {my_driver.Qms():.4f}")                                # Factor de calidad mecánico
# print(f"Kms: {my_driver.Kms:.4f} N/m")                              # Rigidez mecánica
# print("============================\n")                             # Separador visual

# --------------------------------------------
# Calcular y mostrar impedancia y SPL para una frecuencia específica
# --------------------------------------------

freq = params["Fs"]                                                 # Usar la frecuencia de resonancia para la prueba puntual
Z = my_driver.impedance(freq)                                       # Calcula la impedancia compleja a esa frecuencia
print(f"Impedancia a {freq} Hz: {abs(Z):.2f} Ohm (módulo)")         # Imprime el módulo de la impedancia
print(f"SPL Total a {freq} Hz: {my_driver.spl_total(freq):.2f} dB") # Imprime el SPL total a esa frecuencia
print(f"SPL 2pi a {freq} Hz: {my_driver.spl_2pi(freq):.2f} dB")     # Imprime el SPL 2pi a esa frecuencia
print(f"Fase SPL a {freq} Hz: {my_driver.spl_phase(freq):.2f} °")   # Imprime la fase del SPL a esa frecuencia

# --------------------------------------------
# Barrido de frecuencias para simulación de rango completo
# --------------------------------------------

frequencies = np.logspace(np.log10(5), np.log10(20000), 2000)       # Vector de frecuencias de 5 Hz a 1000 Hz (escala logarítmica)

# Calcula la impedancia compleja para cada frecuencia
Z_values = np.array([my_driver.impedance(f) for f in frequencies])
Z_magnitude = np.abs(Z_values)                                      # Módulo de la impedancia
Z_phase = np.angle(Z_values, deg=True)                              # Fase de la impedancia en grados

# Calcula la respuesta SPL estimada para cada frecuencia: total (directividad) + 2pi + fase acústica
SPL_total = np.array([my_driver.spl_total(f) for f in frequencies])
SPL_2pi = np.array([my_driver.spl_2pi(f) for f in frequencies])
SPL_phase = np.array([my_driver.spl_phase(f) for f in frequencies])

# Calcula la velocidad del cono para cada frecuencia (magnitud)
velocities = np.array([abs(my_driver.velocity(f)) for f in frequencies])

# Calcula la excursión pico del cono para cada frecuencia
excursions = velocities / (2 * np.pi * frequencies)                 # Excursión en metros
excursions_mm = excursions * 1000                                   # Excursión en milímetros
excursion_ratio = excursions / my_driver.Xmax                       # Excursión normalizada respecto a Xmax

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

# --------------------------------------------
# Gráfica en panel 2x2 para análisis completo
# --------------------------------------------

fig, axs = plt.subplots(2, 2, figsize=(12, 10))

# === 1. Impedancia y fase eléctrica
axs[0, 0].set_title("Impedancia y Fase Eléctrica")
ax1 = axs[0, 0]
ln1 = ax1.semilogx(frequencies, Z_magnitude, 'b-', label="|Z| [Ohm]")[0]
ax1.set_ylabel("Impedancia [Ohm]", color='b')
ax1.tick_params(axis='y', labelcolor='b')

ax2 = ax1.twinx()
ln2 = ax2.semilogx(frequencies, Z_phase, 'r-', label="∠Z [°]")[0]
ax2.set_ylabel("Fase [°]", color='r')
ax2.tick_params(axis='y', labelcolor='r')

lns1 = [ln1, ln2]
labs1 = [l.get_label() for l in lns1]
ax1.legend(lns1, labs1, loc='best')

# === 2. SPL Total, SPL 2pi y Fase ===
axs[0, 1].set_title("Respuesta SPL y Fase")

ax_spl = axs[0, 1]
ln3 = ax_spl.semilogx(frequencies, SPL_total, label="Total SPL Max (directividad)")[0]
ln4 = ax_spl.semilogx(frequencies, SPL_2pi, '--', label="Total SPL 2pi")[0]
ax_spl.set_ylabel("SPL [dB]", color='b')
ax_spl.tick_params(axis='y', labelcolor='b')

ax_phase = ax_spl.twinx()
ln5 = ax_phase.semilogx(frequencies, SPL_phase, 'g-', label="Total Phase")[0]
ax_phase.set_ylabel("Fase [°]", color='g')
ax_phase.set_ylim(-180, 180)
ax_phase.tick_params(axis='y', labelcolor='g')

lns_spl_phase = [ln3, ln4, ln5]
labs_spl_phase = [l.get_label() for l in lns_spl_phase]
ax_spl.legend(lns_spl_phase, labs_spl_phase, loc='best')

# === 3. Velocidad del cono ===
axs[1, 0].set_title("Velocidad del Cono")
ln6 = axs[1, 0].semilogx(frequencies, velocities, label="Velocidad [m/s]")[0]
axs[1, 0].set_ylabel("Velocidad [m/s]")
axs[1, 0].legend()
axs[1, 0].set_xlabel("Frecuencia [Hz]")

# === 4. Excursión pico y ratio Xmax ===
axs[1, 1].set_title("Excursión pico y relación con Xmax")
ln7 = axs[1, 1].semilogx(frequencies, excursions_mm, label="Excursión [mm]")[0]
ln8 = axs[1, 1].semilogx(frequencies, excursion_ratio, '--', label="Excursión/Xmax")[0]
hline = axs[1, 1].axhline(1, color="red", linestyle=":", label="Límite Xmax")
axs[1, 1].legend()

# --------------------------------------------
# Formato de ejes y ticks
# --------------------------------------------

custom_ticks = [10, 100, 1000, 10000, 15000, 20000]
def fmt_ticks(x, pos):
    if x >= 1000:
        return f"{x/1000:.0f}k"
    else:
        return f"{x:.0f}"

for ax in axs.flat:
    ax.set_xscale('log')
    ax.set_xlim([10, 20000])
    ax.xaxis.set_major_locator(FixedLocator(custom_ticks))
    ax.xaxis.set_minor_locator(LogLocator(base=10, subs='auto'))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(fmt_ticks))
    ax.grid(True, which="both")
    ax.set_xlabel("Frecuencia [Hz]")

ax2.set_xlim([10, 20000])
ax2.xaxis.set_major_locator(FixedLocator(custom_ticks))
ax2.xaxis.set_minor_locator(LogLocator(base=10, subs='auto'))
ax2.xaxis.set_major_formatter(ticker.FuncFormatter(fmt_ticks))

# --------------------------------------------
# Cursores
# --------------------------------------------

def cursor_fmt(sel):
    x = sel.target[0]
    y = sel.target[1]
    if x >= 1000:
        x_label = f"{x/1000:.1f}k"
    else:
        x_label = f"{x:.0f}"
    label = sel.artist.get_label()
    if "|Z|" in label:
        y_unit = "Ω"
    elif "∠Z" in label or "Phase" in label:
        y_unit = "°"
    elif "SPL" in label:
        y_unit = "dB"
    elif "Velocidad" in label:
        y_unit = "m/s"
    elif "Excursión/Xmax" in label:
        y_unit = "(ratio)"
    elif "Excursión" in label:
        y_unit = "mm"
    else:
        y_unit = ""
    sel.annotation.set_text(f"X: {x_label} Hz\nY: {y:.2f} {y_unit}")

all_lines = lns1 + lns_spl_phase + [ln6, ln7, ln8, hline]           # Lista final de líneas (todas Line2D)

cursor = mplcursors.cursor(all_lines, hover=True)
cursor.connect("add", cursor_fmt)

plt.tight_layout()
plt.show()

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

# Fin del script principal
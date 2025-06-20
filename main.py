# --------------------------------------------
# main.py
# Script principal para simular y analizar el comportamiento de un parlante en aire libre.
# --------------------------------------------

# --------------------------------------------
# Importar librerías necesarias
# --------------------------------------------

import numpy as np                              # Para operaciones matemáticas y manejo de arrays
import matplotlib
matplotlib.use("TkAgg")                         # Fuerza el uso del backend TkAgg para mostrar gráficos en ventana
import matplotlib.pyplot as plt                 # Para graficar resultados
from core.driver import Driver                  # Importa la clase Driver definida en core/driver.py

# --------------------------------------------
# Definir parámetros del altavoz
# --------------------------------------------

params = {
    "Fs": 40,           # Frecuencia de resonancia [Hz]
    "Vas": 50,          # Volumen de aire equivalente [litros]
    "Qts": 0.35,        # Factor de calidad total
    "Qes": 0.4,         # Factor de calidad eléctrico
    "Re": 6.0,          # Resistencia de la bobina [Ohm]
    "Bl": 7.5,          # Producto flujo-Bobina [N/A]
    "Sd": 0.02,         # Área efectiva del diafragma [m²]
    "Le": 0.0005        # Inductancia de la bobina [Henrios]
}

# Crear una instancia de Driver con estos parámetros
my_driver = Driver(params)

# --------------------------------------------
# Mostrar parámetros derivados en consola
# --------------------------------------------

print(f"Mms: {my_driver.Mms:.4f} kg")           # Masa móvil del diafragma
print(f"Cms: {my_driver.Cms:.6f} m/N")          # Complianza mecánica
print(f"Rms: {my_driver.Rms:.4f} kg/s")         # Resistencia mecánica
print(f"Qms: {my_driver.Qms():.4f}")            # Factor de calidad mecánico
print(f"Kms: {my_driver.derive_Kms():.4f} N/m") # Rigidez mecánica
print("============================\n")            # Separador visual

# --------------------------------------------
# Calcular y mostrar impedancia y SPL para una frecuencia específica
# --------------------------------------------

freq = params["Fs"]                             # Usar la frecuencia de resonancia para la prueba puntual
Z = my_driver.impedance(freq)                   # Calcula la impedancia compleja a esa frecuencia
print(f"Impedancia a {freq} Hz: {abs(Z):.2f} Ohm (módulo)")  # Imprime el módulo de la impedancia
print(f"SPL a {freq} Hz: {my_driver.spl_response(freq):.2f} dB")  # Imprime el SPL estimado

# --------------------------------------------
# Barrido de frecuencias para simulación de rango completo
# --------------------------------------------

frequencies = np.logspace(np.log10(5), np.log10(1000), 500)  # Vector de frecuencias de 5 Hz a 1000 Hz (escala logarítmica)

# Calcula la impedancia compleja para cada frecuencia
Z_values = np.array([my_driver.impedance(f) for f in frequencies])
Z_magnitude = np.abs(Z_values)                  # Módulo de la impedancia
Z_phase = np.angle(Z_values, deg=True)          # Fase de la impedancia en grados

# Calcula la respuesta SPL estimada para cada frecuencia
SPL_values = np.array([my_driver.spl_response(f) for f in frequencies])

# Calcula la velocidad del cono para cada frecuencia (magnitud)
velocities = np.array([abs(my_driver.velocity(f)) for f in frequencies])

# Calcula la excursión pico del cono para cada frecuencia
excursions = velocities / (2 * np.pi * frequencies)     # Excursión en metros
excursions_mm = excursions * 1000                       # Excursión en milímetros
excursion_ratio = excursions / my_driver.Xmax           # Excursión normalizada respecto a Xmax

# --------------------------------------------
# Gráfica en panel 2x2 para análisis completo
# --------------------------------------------

fig, axs = plt.subplots(2, 2, figsize=(12, 10))         # Crea una figura con 4 subgráficas (2x2)

# 1. Impedancia (módulo y fase)
axs[0, 0].set_title("Impedancia y Fase")
axs[0, 0].semilogx(frequencies, Z_magnitude, label="|Z| [Ohm]")   # Gráfica del módulo de la impedancia
axs[0, 0].semilogx(frequencies, Z_phase, label="∠Z [°]")          # Gráfica de la fase de la impedancia
axs[0, 0].set_xlabel("Frecuencia [Hz]")
axs[0, 0].set_ylabel("Impedancia / Fase")
axs[0, 0].legend()
axs[0, 0].grid(True, which="both")

# 2. SPL
axs[0, 1].set_title("Respuesta SPL Estimada")
axs[0, 1].semilogx(frequencies, SPL_values, label="SPL [dB]")     # Gráfica de la respuesta SPL
axs[0, 1].set_xlabel("Frecuencia [Hz]")
axs[0, 1].set_ylabel("SPL [dB]")
axs[0, 1].legend()
axs[0, 1].grid(True, which="both")

# 3. Velocidad del cono
axs[1, 0].set_title("Velocidad del Cono [m/s]")
axs[1, 0].semilogx(frequencies, velocities)                       # Gráfica de la velocidad del cono
axs[1, 0].set_xlabel("Frecuencia [Hz]")
axs[1, 0].set_ylabel("Velocidad [m/s]")
axs[1, 0].grid(True, which="both")

# 4. Excursión pico y relación con Xmax
axs[1, 1].set_title("Excursión pico y relación con Xmax")
axs[1, 1].semilogx(frequencies, excursions_mm, label="Excursión [mm]")      # Excursión en mm
axs[1, 1].semilogx(frequencies, excursion_ratio, "--", label="Excursión/Xmax")  # Excursión normalizada
axs[1, 1].axhline(1, color="red", linestyle=":", label="Límite Xmax")       # Línea horizontal en Xmax
axs[1, 1].set_xlabel("Frecuencia [Hz]")
axs[1, 1].set_ylabel("Excursión [mm] / Ratio")
axs[1, 1].legend()
axs[1, 1].grid(True, which="both")

# Ajusta márgenes y muestra las gráficas
plt.tight_layout()
plt.show()

# --------------------------------------------
# Fin del script principal

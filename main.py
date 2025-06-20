# --------------------------------------------
# --------------------------------------------
# main.py
# --------------------------------------------
# --------------------------------------------

# --------------------------------------------
# Importar librerías necesarias
# --------------------------------------------

import numpy as np                                                          # Para operaciones matemáticas y arrays
import matplotlib
matplotlib.use("TkAgg")                                                     # Fuerza el backend que abre ventana
import matplotlib.pyplot as plt                                             # Para graficar
from core.driver import Driver                                              # Importa la clase Driver

# --------------------------------------------
# Definir parámetros del altavoz
# --------------------------------------------

params = {
    "Fs": 40,                                                               # Frecuencia de resonancia [Hz]
    "Vas": 50,                                                              # Volumen de aire equivalente [litros]
    "Qts": 0.35,                                                            # Factor de calidad total
    "Qes": 0.4,                                                             # Factor de calidad eléctrico
    "Re": 6.0,                                                              # Resistencia de la bobina [Ohm]
    "Bl": 7.5,                                                              # Producto flujo-Bobina [N/A]
    "Sd": 0.02,                                                             # Área efectiva del diafragma [m²]
    "Le": 0.0005                                                            # Inductancia de la bobina [Henrios]
}

# Crear una instancia de Driver con estos parámetros
my_driver = Driver(params)

# --------------------------------------------
# Mostrar parámetros derivados en consola
# --------------------------------------------

print(f"Mms: {my_driver.Mms:.4f} kg")                                       # Masa móvil del diafragma
print(f"Cms: {my_driver.Cms:.6f} m/N")                                      # Complianza mecánica
print(f"Rms: {my_driver.Rms:.4f} kg/s")                                     # Resistencia mecánica
print(f"Qms: {my_driver.Qms():.4f}")                                        # Factor de calidad mecánico
print(f"Kms: {my_driver.derive_Kms():.4f} N/m")
print("============================\n")     

# # --------------------------------------------
# # Prueba puntual
# # --------------------------------------------
# freq = 40  # Hz
# Z = my_driver.impedance(freq)
# print(f"Impedancia a {freq} Hz: {abs(Z):.2f} Ohm")
# print(f"SPL a {freq} Hz: {my_driver.spl_response(freq):.2f} dB")

# --------------------------------------------
# Calcular y mostrar impedancia y SPL para una frecuencia específica
# --------------------------------------------

freq = params["Fs"]                                                                   # Hz
Z = my_driver.impedance(freq)                                               # Impedancia compleja a esa frecuencia
print(f"Impedancia a {freq} Hz: {abs(Z):.2f} Ohm (módulo)")                 # Módulo
print(f"SPL a {freq} Hz: {my_driver.spl_response(freq):.2f} dB")            # SPL estimado

# --------------------------------------------
# Barrido de frecuencias para simulación de rango completo
# --------------------------------------------

# Genera un vector de 500 puntos espaciados logarítmicamente de ~5 Hz a 1000 Hz
frequencies = np.logspace(np.log10(5), np.log10(1000), 500)

# Calcula impedancia compleja para cada frecuencia
Z_values = np.array([my_driver.impedance(f) for f in frequencies])
Z_magnitude = np.abs(Z_values)                                              # Módulo de la impedancia
Z_phase = np.angle(Z_values, deg=True)                                      # Fase en grados

# Calcula la respuesta SPL estimada para cada frecuencia
SPL_values = np.array([my_driver.spl_response(f) for f in frequencies])

# Velocidad del cono y excursión pico normalizada a Xmax
velocities = np.array([abs(my_driver.velocity(f)) for f in frequencies])

# Excursión pico (m), en mm y normalizada
excursions = velocities / (2 * np.pi * frequencies)                         # m
excursions_mm = excursions * 1000                                           # mm
excursion_ratio = excursions / my_driver.Xmax                               # Relación con Xmax

# --------------------------------------------
# Gráfica en panel 2x2 para análisis completo
# --------------------------------------------

fig, axs = plt.subplots(2, 2, figsize=(12, 10))

# 1. Impedancia (módulo y fase)
axs[0, 0].set_title("Impedancia y Fase")
axs[0, 0].semilogx(frequencies, Z_magnitude, label="|Z| [Ohm]")
axs[0, 0].semilogx(frequencies, Z_phase, label="∠Z [°]")
axs[0, 0].set_xlabel("Frecuencia [Hz]")
axs[0, 0].set_ylabel("Impedancia / Fase")
axs[0, 0].legend()
axs[0, 0].grid(True, which="both")

# 2. SPL
axs[0, 1].set_title("Respuesta SPL Estimada")
axs[0, 1].semilogx(frequencies, SPL_values, label="SPL [dB]")
axs[0, 1].set_xlabel("Frecuencia [Hz]")
axs[0, 1].set_ylabel("SPL [dB]")
axs[0, 1].legend()
axs[0, 1].grid(True, which="both")

# 3. Velocidad del cono
axs[1, 0].set_title("Velocidad del Cono [m/s]")
axs[1, 0].semilogx(frequencies, velocities)
axs[1, 0].set_xlabel("Frecuencia [Hz]")
axs[1, 0].set_ylabel("Velocidad [m/s]")
axs[1, 0].grid(True, which="both")

# 4. Excursión pico y relación con Xmax
axs[1, 1].set_title("Excursión pico y relación con Xmax")
axs[1, 1].semilogx(frequencies, excursions_mm, label="Excursión [mm]")
axs[1, 1].semilogx(frequencies, excursion_ratio, "--", label="Excursión/Xmax")
axs[1, 1].axhline(1, color="red", linestyle=":", label="Límite Xmax")
axs[1, 1].set_xlabel("Frecuencia [Hz]")
axs[1, 1].set_ylabel("Excursión [mm] / Ratio")
axs[1, 1].legend()
axs[1, 1].grid(True, which="both")

# Ajusta márgenes y muestra las gráficas
plt.tight_layout()
plt.show()

# --------------------------------------------
# Fin del script principal  

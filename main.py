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
from core.driver import Driver                                              # Importa tu clase Driver personalizada

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

# --------------------------------------------
# Calcular y mostrar impedancia y SPL para una frecuencia específica
# --------------------------------------------

freq = 40                                                                   # Hz
Z = my_driver.impedance(freq)                                               # Impedancia compleja a esa frecuencia
print(f"Impedancia a {freq} Hz: {abs(Z):.2f} Ohm (módulo)")                 # Módulo
print(f"SPL a {freq} Hz: {my_driver.spl_response(freq):.2f} dB")            # SPL estimado

# --------------------------------------------
# Barrido de frecuencias para simulación de rango completo
# --------------------------------------------

# Genera un vector de 500 puntos log-espaciados de ~5 Hz a 1000 Hz
frequencies = np.logspace(0.7, 3, 500)

# Calcula impedancia compleja para cada frecuencia
Z_values = np.array([my_driver.impedance(f) for f in frequencies])
Z_magnitude = np.abs(Z_values)                # Módulo de la impedancia
Z_phase = np.angle(Z_values, deg=True)        # Fase en grados

# Calcula la respuesta SPL estimada para cada frecuencia
SPL_values = np.array([my_driver.spl_response(f) for f in frequencies])

# --------------------------------------------
# Graficar resultados con Matplotlib
# --------------------------------------------

# Crea una figura con dos subgráficas (una para impedancia, otra para SPL)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Gráfica de Impedancia
ax1.set_title("Impedancia del Driver")
ax1.semilogx(frequencies, Z_magnitude, label="|Z| [Ohm]")  # Módulo
ax1.semilogx(frequencies, Z_phase, label="∠Z [°]")         # Fase
ax1.set_xlabel("Frecuencia [Hz]")
ax1.set_ylabel("Impedancia / Fase")
ax1.grid(True, which="both")
ax1.legend()

# Gráfica de Respuesta SPL
ax2.set_title("Respuesta SPL estimada")
ax2.semilogx(frequencies, SPL_values, label="SPL [dB]")
ax2.set_xlabel("Frecuencia [Hz]")
ax2.set_ylabel("SPL [dB]")
ax2.grid(True, which="both")
ax2.legend()

# Ajusta márgenes y muestra las gráficas
plt.tight_layout()
plt.show()

# Test script para BandpassIsobaricBox
import numpy as np
import matplotlib.pyplot as plt
from core.bandpass_isobaric import BandpassIsobaricBox

# Parámetros de ejemplo
params = {
    'rho0': 1.21,              # Densidad del aire [kg/m³]
    'c0': 343,                 # Velocidad del sonido [m/s]
    'BL': 10.0,                # Factor motor [T·m]
    'Re': 5.0,                 # Resistencia DC [Ω]
    'Red': 0.5,                # Resistencia adicional [Ω]
    'Qes': 0.4,                # Factor de calidad eléctrico
    'Qms': 3.0,                # Factor de calidad mecánico
    'fs': 30.0,                # Frecuencia de resonancia [Hz]
    'Lvc': 0.1,                # Inductancia de la bobina [mH]
    'S': 0.01,                 # Área del diafragma [m²]
    'Vab': 0.150,              # Volumen cámara trasera [m³]
    'fp': 27.36,               # Frecuencia de sintonía [Hz]
    'dd': 0.3366,              # Diámetro diafragma [m]
    'dp': 0.2,                 # Diámetro puerto [m]
    'B': 1.0,                  # Factor B (parámetro adicional)
    'Mmd': 0.015,              # Masa del diafragma [kg]
    'V0': 2.83,                # Voltaje de entrada [V]
}

# Crear objeto bandpass
bandpass = BandpassIsobaricBox(params)

# Rango de frecuencias
frequencies = np.logspace(np.log10(10), np.log10(1000), 500)

# Simular
results = bandpass.simulate(frequencies)

# Graficar resultados
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))

# SPL
ax1.semilogx(results["freq"], results["SPL"])
ax1.set_xlabel("Frecuencia [Hz]")
ax1.set_ylabel("SPL [dB]")
ax1.set_title("Respuesta en Frecuencia")
ax1.grid(True)

# Impedancia
ax2.semilogx(results["freq"], results["Zt"])
ax2.set_xlabel("Frecuencia [Hz]")
ax2.set_ylabel("Impedancia [Ω]")
ax2.set_title("Impedancia Eléctrica")
ax2.grid(True)

# Desplazamiento
ax3.semilogx(results["freq"], results["DEZ"])
ax3.set_xlabel("Frecuencia [Hz]")
ax3.set_ylabel("Desplazamiento [mm]")
ax3.set_title("Desplazamiento del Cono")
ax3.grid(True)

# Group Delay
ax4.semilogx(results["freq"], results["groupdelay"])
ax4.set_xlabel("Frecuencia [Hz]")
ax4.set_ylabel("Group Delay [ms]")
ax4.set_title("Retardo de Grupo")
ax4.grid(True)

plt.tight_layout()
plt.show()

print("Simulación de Bandpass Isobárico completada!")
print(f"Frecuencia de sintonía: {params['fp']} Hz")
print(f"Volumen cámara trasera: {params['Vab']*1000:.1f} L")

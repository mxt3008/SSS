#!/usr/bin/env python3
# Test para análisis de resonancias en sistema bandpass isobárico

import numpy as np
import matplotlib.pyplot as plt
from core.bandpass_isobaric import BandpassIsobaricBox

print("=== ANÁLISIS DE RESONANCIAS BANDPASS ISOBÁRICO ===")
print()

# Parámetros típicos de un sistema bandpass isobárico
params_bandpass = {
    'rho0': 1.2,              # Densidad del aire [kg/m³]
    'c0': 344,                # Velocidad del sonido [m/s]
    'BL': 18.1,               # Factor motor [T·m]
    'Re': 5.3,                # Resistencia DC [Ω]
    'Red': 3.77,              # Resistencia adicional [Ω]
    'Qes': 0.34,              # Factor de calidad eléctrico
    'Qms': 4.5,               # Factor de calidad mecánico
    'fs': 52,                 # Frecuencia de resonancia [Hz]
    'Lvc': 0.1,               # Inductancia de la bobina [mH]
    'S': 0.055,               # Área del diafragma [m²]
    'Vab': 0.025,             # Volumen cámara trasera [m³] (25L)
    'Vf': 0.015,              # Volumen cámara frontal [m³] (15L)
    'fp': 45,                 # Frecuencia de sintonía [Hz]
    'dd': 0.20,               # Diámetro diafragma [m]
    'dp': 0.10,               # Diámetro puerto [m]
    'Lp': 0.15,               # Longitud puerto [m]
    'B': 0.8333,              # Factor B
    'Mmd': 0.015,             # Masa del diafragma [kg]
    'V0': 2.83,               # Voltaje de entrada [V]
}

print("PARÁMETROS DEL SISTEMA:")
print(f"fs (driver) = {params_bandpass['fs']} Hz")
print(f"fp (puerto) = {params_bandpass['fp']} Hz")
print(f"Vab (trasera) = {params_bandpass['Vab']*1000:.1f} L")
print(f"Vf (frontal) = {params_bandpass['Vf']*1000:.1f} L")
print(f"Qes = {params_bandpass['Qes']}")
print(f"Qms = {params_bandpass['Qms']}")
print()

# Calcular frecuencias de resonancia teóricas
# 1. Resonancia del driver en aire libre
fs_libre = params_bandpass['fs']

# 2. Resonancia del puerto
fp_puerto = params_bandpass['fp']

# 3. Resonancia del driver en la cámara trasera
# fs_caja = fs * sqrt(1 + Vas/Vab) donde Vas se puede estimar
rho0 = params_bandpass['rho0']
c0 = params_bandpass['c0']
Vab = params_bandpass['Vab']
S = params_bandpass['S']

# Estimar Vas desde los parámetros TS
BL = params_bandpass['BL']
Re = params_bandpass['Re']
Qes = params_bandpass['Qes']
Mms = Qes*(BL**2)/(2*np.pi*fs_libre*Re)
Cms = 1/(Mms*(2*np.pi*fs_libre)**2)
Vas_estimado = rho0 * c0**2 * Cms * S**2

fs_caja = fs_libre * np.sqrt(1 + Vas_estimado/Vab)

print("FRECUENCIAS DE RESONANCIA TEÓRICAS:")
print(f"1. fs libre (driver) = {fs_libre:.1f} Hz")
print(f"2. fp puerto = {fp_puerto:.1f} Hz") 
print(f"3. fs caja (driver en Vab) = {fs_caja:.1f} Hz")
print(f"   (Vas estimado = {Vas_estimado*1000:.1f} L)")
print()

# Crear el sistema bandpass
bandpass = BandpassIsobaricBox(params_bandpass)

# Simular en un rango amplio para ver todas las resonancias
frequencies = np.logspace(np.log10(10), np.log10(200), 1000)
results = bandpass.simulate(frequencies)

# Encontrar picos en la impedancia
impedancia = results["Zt"]
freq_array = results["freq"]

# Encontrar máximos locales
from scipy.signal import find_peaks
peaks, _ = find_peaks(impedancia, height=np.max(impedancia)*0.1, distance=50)

print("PICOS ENCONTRADOS EN LA SIMULACIÓN:")
print(f"Total de picos detectados: {len(peaks)}")
for i, peak in enumerate(peaks):
    freq_pico = freq_array[peak]
    z_pico = impedancia[peak]
    print(f"Pico {i+1}: f = {freq_pico:.1f} Hz, Z = {z_pico:.1f} Ω")
print()

if len(peaks) < 3:
    print("⚠️  PROBLEMA DETECTADO: Solo se encontraron", len(peaks), "picos")
    print("   Un sistema bandpass isobárico debería tener 3 picos de impedancia")
    print()
    print("POSIBLES CAUSAS:")
    print("1. Frecuencias de resonancia muy cercanas (se superponen)")
    print("2. Factor Q muy alto (picos muy estrechos)")
    print("3. Rango de frecuencias insuficiente") 
    print("4. Error en el modelo del circuito equivalente")
    print("5. Parámetros mal calculados")
else:
    print("✓ Sistema funcionando correctamente con", len(peaks), "picos")

# Crear gráfica para análisis visual
plt.figure(figsize=(12, 8))

plt.subplot(2, 2, 1)
plt.semilogx(freq_array, impedancia)
plt.plot(freq_array[peaks], impedancia[peaks], 'ro', markersize=8)
plt.grid(True)
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Impedancia [Ω]')
plt.title('Impedancia - Picos detectados')
plt.legend(['Impedancia', 'Picos'])

plt.subplot(2, 2, 2)
plt.semilogx(freq_array, results["SPL"])
plt.grid(True)
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('SPL [dB]')
plt.title('Respuesta en Frecuencia')

plt.subplot(2, 2, 3)
plt.semilogx(freq_array, results["ZtΦ"])
plt.grid(True)
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Fase [°]')
plt.title('Fase de Impedancia')

plt.subplot(2, 2, 4)
plt.semilogx(freq_array, results["DEZ"])
plt.grid(True)
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Desplazamiento [mm]')
plt.title('Desplazamiento del Cono')

plt.tight_layout()
plt.savefig('analisis_bandpass.png', dpi=150, bbox_inches='tight')
plt.show()

print("Gráfica guardada como 'analisis_bandpass.png'")
print()
print("=== RECOMENDACIONES ===")
if len(peaks) < 3:
    print("Para corregir el problema:")
    print("1. Verificar que fp esté entre las dos resonancias del driver")
    print("2. Ajustar los volúmenes Vab y Vf")
    print("3. Revisar los factores Q (Qes, Qms)")
    print("4. Ampliar el rango de frecuencias de simulación")

#!/usr/bin/env python3
# Test con parámetros optimizados para bandpass isobárico

import numpy as np
import matplotlib.pyplot as plt
from core.bandpass_isobaric import BandpassIsobaricBox

print("=== TEST BANDPASS CON PARÁMETROS OPTIMIZADOS ===")
print()

# Parámetros típicos optimizados para 3 resonancias claras
params_optimized = {
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
    'Vab': 0.030,             # Volumen cámara trasera AUMENTADO [m³] (30L)
    'Vf': 0.010,              # Volumen cámara frontal REDUCIDO [m³] (10L)
    'fp': 65,                 # Frecuencia de sintonía AUMENTADA [Hz] (entre fs y fs_caja)
    'dd': 0.20,               # Diámetro diafragma [m]
    'dp': 0.08,               # Diámetro puerto REDUCIDO [m] 
    'Lp': 0.12,               # Longitud puerto REDUCIDA [m]
    'B': 0.8333,              # Factor B
    'Mmd': 0.015,             # Masa del diafragma [kg]
    'V0': 2.83,               # Voltaje de entrada [V]
}

print("PARÁMETROS OPTIMIZADOS:")
print(f"fs (driver) = {params_optimized['fs']} Hz")
print(f"fp (puerto) = {params_optimized['fp']} Hz")
print(f"Vab (trasera) = {params_optimized['Vab']*1000:.1f} L")
print(f"Vf (frontal) = {params_optimized['Vf']*1000:.1f} L")
print()

# Calcular frecuencias teóricas con nuevos parámetros
fs_libre = params_optimized['fs']
fp_puerto = params_optimized['fp']

# Estimar fs en caja con Vab mayor
rho0 = params_optimized['rho0']
c0 = params_optimized['c0']
Vab = params_optimized['Vab']
S = params_optimized['S']
BL = params_optimized['BL']
Re = params_optimized['Re']
Qes = params_optimized['Qes']

Mms = Qes*(BL**2)/(2*np.pi*fs_libre*Re)
Cms = 1/(Mms*(2*np.pi*fs_libre)**2)
Vas_estimado = rho0 * c0**2 * Cms * S**2
fs_caja = fs_libre * np.sqrt(1 + Vas_estimado/Vab)

print("FRECUENCIAS TEÓRICAS CON PARÁMETROS OPTIMIZADOS:")
print(f"1. fs libre = {fs_libre:.1f} Hz")
print(f"2. fp puerto = {fp_puerto:.1f} Hz") 
print(f"3. fs caja = {fs_caja:.1f} Hz")
print(f"   Secuencia esperada: {fs_libre:.1f} < {fp_puerto:.1f} < {fs_caja:.1f}")
print()

# Comprobar que fp esté entre fs y fs_caja
if fs_libre < fp_puerto < fs_caja:
    print("✓ fp está correctamente entre fs y fs_caja")
else:
    print("⚠️  fp NO está entre fs y fs_caja")
print()

# Simular sistema
bandpass = BandpassIsobaricBox(params_optimized)
frequencies = np.logspace(np.log10(10), np.log10(200), 1000)
results = bandpass.simulate(frequencies)

# Detectar picos
from scipy.signal import find_peaks
impedancia = results["Zt"]
freq_array = results["freq"]

# Buscar picos con criterios más flexibles
peaks, props = find_peaks(impedancia, 
                         height=np.max(impedancia)*0.05,  # 5% del máximo
                         distance=30,  # Separación mínima
                         prominence=1.0)  # Prominencia mínima

print("PICOS DETECTADOS CON PARÁMETROS OPTIMIZADOS:")
print(f"Total de picos: {len(peaks)}")
for i, peak in enumerate(peaks):
    freq_pico = freq_array[peak]
    z_pico = impedancia[peak]
    prominence = props['prominences'][i] if 'prominences' in props else 0
    print(f"Pico {i+1}: f = {freq_pico:.1f} Hz, Z = {z_pico:.1f} Ω, prom = {prominence:.1f}")
print()

# Análisis de calidad
if len(peaks) >= 3:
    print("✓ ¡ÉXITO! Se detectaron 3 o más picos de resonancia")
    print("El modelo bandpass isobárico funciona correctamente")
else:
    print(f"⚠️  Aún faltan picos: solo {len(peaks)} de 3 esperados")
    print("Posibles ajustes:")
    print("- Aumentar más el volumen Vab")
    print("- Reducir más el diámetro del puerto")
    print("- Ajustar fp para estar más centrado entre resonancias")

# Gráfica mejorada
plt.figure(figsize=(15, 10))

plt.subplot(2, 3, 1)
plt.semilogx(freq_array, impedancia, 'b-', linewidth=2)
plt.plot(freq_array[peaks], impedancia[peaks], 'ro', markersize=10, markeredgecolor='black')
plt.axvline(fs_libre, color='green', linestyle='--', alpha=0.7, label=f'fs libre ({fs_libre:.1f} Hz)')
plt.axvline(fp_puerto, color='orange', linestyle='--', alpha=0.7, label=f'fp puerto ({fp_puerto:.1f} Hz)')
plt.axvline(fs_caja, color='red', linestyle='--', alpha=0.7, label=f'fs caja ({fs_caja:.1f} Hz)')
plt.grid(True, alpha=0.3)
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Impedancia [Ω]')
plt.title('Impedancia - Resonancias Detectadas')
plt.legend()

plt.subplot(2, 3, 2)
plt.semilogx(freq_array, results["SPL"], 'g-', linewidth=2)
plt.grid(True, alpha=0.3)
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('SPL [dB]')
plt.title('Respuesta en Frecuencia')

plt.subplot(2, 3, 3)
plt.semilogx(freq_array, results["ZtΦ"], 'm-', linewidth=2)
plt.grid(True, alpha=0.3)
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Fase [°]')
plt.title('Fase de Impedancia')

plt.subplot(2, 3, 4)
plt.semilogx(freq_array, results["DEZ"], 'r-', linewidth=2)
plt.grid(True, alpha=0.3)
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Desplazamiento [mm]')
plt.title('Desplazamiento del Cono')

plt.subplot(2, 3, 5)
# Zoom en la región de interés
zoom_mask = (freq_array >= 20) & (freq_array <= 150)
plt.plot(freq_array[zoom_mask], impedancia[zoom_mask], 'b-', linewidth=2)
peak_mask = [(p in np.where(zoom_mask)[0]) for p in peaks]
if any(peak_mask):
    peaks_zoom = [peaks[i] for i, mask in enumerate(peak_mask) if mask]
    plt.plot(freq_array[peaks_zoom], impedancia[peaks_zoom], 'ro', markersize=10)
plt.axvline(fs_libre, color='green', linestyle='--', alpha=0.7)
plt.axvline(fp_puerto, color='orange', linestyle='--', alpha=0.7)
plt.axvline(fs_caja, color='red', linestyle='--', alpha=0.7)
plt.grid(True, alpha=0.3)
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Impedancia [Ω]')
plt.title('Zoom: Región de Resonancias')

plt.subplot(2, 3, 6)
# Análisis de prominencia de picos
if len(peaks) > 0:
    prom = props.get('prominences', np.ones(len(peaks)))
    plt.bar(range(len(peaks)), prom, color='skyblue', edgecolor='navy')
    plt.xlabel('Número de Pico')
    plt.ylabel('Prominencia')
    plt.title('Prominencia de Picos')
    plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('bandpass_optimizado.png', dpi=150, bbox_inches='tight')
plt.show()

print()
print("Gráfica guardada como 'bandpass_optimizado.png'")

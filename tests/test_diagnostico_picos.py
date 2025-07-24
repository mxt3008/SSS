#!/usr/bin/env python3
"""
DIAGNÓSTICO DE LOS PICOS - ¿DÓNDE CARAJO ESTÁN?
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from core.driver import Driver
from core.sealed import SealedBox
from core.bassreflex import BassReflexBox

# PARÁMETROS DE MAIN.PY
params = {
    "Fs": 52, 
    "Mms": 0.065, 
    "Vas": 62, 
    "Qts": 0.32, 
    "Qes": 0.34, 
    "Qms": 4.5,
    "Re": 5.3, 
    "Bl": 18.1, 
    "Sd": 0.055, 
    "Le": 1.5e-3, 
    "Xmax": 7.5
}

freq = np.logspace(1, 3, 2000)  # MUY alta resolución

print("🔍 DIAGNÓSTICO: ¿DÓNDE ESTÁN LOS PICOS?")

# CONFIGURAR
bassreflex = BassReflexBox(30, 0.01, 0.12)
driver_br = Driver(params, enclosure=bassreflex)

print(f"Frecuencia del puerto: {bassreflex.fp:.1f} Hz")

# CALCULAR IMPEDANCIA
Z_br = driver_br.impedance(freq)
Z_br_mag = np.abs(Z_br)

print(f"Rango de impedancia: {np.min(Z_br_mag):.1f} - {np.max(Z_br_mag):.1f} Ω")

# BUSCAR PICOS REALES
print("\n🔍 BUSCANDO PICOS EN LA IMPEDANCIA:")

# Encontrar máximos locales
from scipy.signal import find_peaks
peaks, properties = find_peaks(Z_br_mag, height=20, distance=50)

print(f"Picos encontrados: {len(peaks)}")
for i, peak_idx in enumerate(peaks):
    print(f"  Pico {i+1}: {freq[peak_idx]:.1f} Hz, {Z_br_mag[peak_idx]:.1f} Ω")

# BUSCAR MÍNIMOS (valles)
valleys, _ = find_peaks(-Z_br_mag, distance=50)
print(f"\nValles encontrados: {len(valleys)}")
for i, valley_idx in enumerate(valleys):
    print(f"  Valle {i+1}: {freq[valley_idx]:.1f} Hz, {Z_br_mag[valley_idx]:.1f} Ω")

# GRÁFICA DIAGNÓSTICA
plt.figure(figsize=(12, 8))
plt.semilogx(freq, Z_br_mag, 'r-', linewidth=2, label='Bass-reflex')
plt.axvline(x=bassreflex.fp, color='orange', linestyle='--', linewidth=2, label=f'Puerto ({bassreflex.fp:.0f} Hz)')

# Marcar picos encontrados
for peak_idx in peaks:
    plt.plot(freq[peak_idx], Z_br_mag[peak_idx], 'ro', markersize=10, markerfacecolor='yellow', markeredgecolor='red')
    plt.annotate(f'{freq[peak_idx]:.0f}Hz', xy=(freq[peak_idx], Z_br_mag[peak_idx]), 
                xytext=(10, 10), textcoords='offset points', fontweight='bold')

# Marcar valles
for valley_idx in valleys:
    plt.plot(freq[valley_idx], Z_br_mag[valley_idx], 'bo', markersize=8, markerfacecolor='cyan', markeredgecolor='blue')
    plt.annotate(f'{freq[valley_idx]:.0f}Hz', xy=(freq[valley_idx], Z_br_mag[valley_idx]), 
                xytext=(10, -15), textcoords='offset points', fontweight='bold')

plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Impedancia [Ω]')
plt.title('DIAGNÓSTICO: ¿DÓNDE ESTÁN LOS PICOS DEL BASS-REFLEX?')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xlim([20, 1000])

plt.tight_layout()
plt.savefig('outputs/diagnostico_picos.png', dpi=300, bbox_inches='tight')
print(f"\n📊 Diagnóstico guardado: outputs/diagnostico_picos.png")

# VERIFICAR QUE EL BASS-REFLEX ESTÁ SIENDO DETECTADO
print(f"\n🔍 VERIFICACIÓN DEL MODELO:")
print(f"Tipo de enclosure: {type(driver_br.enclosure)}")
print(f"¿Tiene fp? {hasattr(driver_br.enclosure, 'fp')}")
print(f"¿Es BassReflex? {'BassReflex' in driver_br.enclosure.__class__.__name__}")

if len(peaks) < 2:
    print(f"\n❌ PROBLEMA: Solo se encontraron {len(peaks)} picos")
    print("❌ Un bass-reflex DEBE tener DOS picos distintivos")
    print("❌ EL MODELO ESTÁ MAL - NECESITA CORRECCIÓN")
else:
    print(f"\n✅ ENCONTRADOS {len(peaks)} picos - MODELO CORRECTO")

#!/usr/bin/env python3
"""
DIAGNÓSTICO SIMPLE - SIN SCIPY
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

freq = np.logspace(1, 3, 1000)

print("🔍 DIAGNÓSTICO SIMPLE: ¿HAY PICOS?")

# CONFIGURAR
bassreflex = BassReflexBox(30, 0.01, 0.12)
driver_br = Driver(params, enclosure=bassreflex)

print(f"Frecuencia del puerto: {bassreflex.fp:.1f} Hz")

# CALCULAR IMPEDANCIA
Z_br = driver_br.impedance(freq)
Z_br_mag = np.abs(Z_br)

print(f"Rango de impedancia: {np.min(Z_br_mag):.1f} - {np.max(Z_br_mag):.1f} Ω")

# BUSCAR PICOS MANUALMENTE
print("\n🔍 BUSCANDO PICOS MANUALMENTE:")

# Buscar máximos locales simple
picos = []
for i in range(2, len(Z_br_mag)-2):
    if (Z_br_mag[i] > Z_br_mag[i-1] and Z_br_mag[i] > Z_br_mag[i+1] and
        Z_br_mag[i] > Z_br_mag[i-2] and Z_br_mag[i] > Z_br_mag[i+2]):
        if Z_br_mag[i] > 50:  # Solo picos significativos
            picos.append((freq[i], Z_br_mag[i]))

print(f"Picos encontrados: {len(picos)}")
for i, (f_pico, z_pico) in enumerate(picos):
    print(f"  Pico {i+1}: {f_pico:.1f} Hz, {z_pico:.1f} Ω")

# BUSCAR MÍNIMOS
valles = []
for i in range(2, len(Z_br_mag)-2):
    if (Z_br_mag[i] < Z_br_mag[i-1] and Z_br_mag[i] < Z_br_mag[i+1] and
        Z_br_mag[i] < Z_br_mag[i-2] and Z_br_mag[i] < Z_br_mag[i+2]):
        if freq[i] > 40 and freq[i] < 200:  # En rango relevante
            valles.append((freq[i], Z_br_mag[i]))

print(f"Valles encontrados: {len(valles)}")
for i, (f_valle, z_valle) in enumerate(valles):
    print(f"  Valle {i+1}: {f_valle:.1f} Hz, {z_valle:.1f} Ω")

# VALORES ESPECÍFICOS
idx_fs = np.argmin(np.abs(freq - 52))
idx_fp = np.argmin(np.abs(freq - bassreflex.fp))

print(f"\n🎯 VALORES ESPECÍFICOS:")
print(f"@ 52 Hz (Fs): {Z_br_mag[idx_fs]:.1f} Ω")
print(f"@ {bassreflex.fp:.1f} Hz (fp): {Z_br_mag[idx_fp]:.1f} Ω")

# VERIFICAR MODELO
print(f"\n🔍 VERIFICACIÓN DEL MODELO:")
print(f"Tipo de enclosure: {type(driver_br.enclosure).__name__}")
print(f"¿Es BassReflex? {'BassReflex' in type(driver_br.enclosure).__name__}")

if len(picos) < 2:
    print(f"\n❌ PROBLEMA CRÍTICO: Solo {len(picos)} picos encontrados")
    print("❌ Un bass-reflex DEBE mostrar DOS picos bien definidos")
    print("❌ EL MODELO ESTÁ ROTO")
else:
    print(f"\n✅ {len(picos)} picos encontrados - podría estar bien")

print("\n📊 Generando gráfica...")

plt.figure(figsize=(12, 8))
plt.semilogx(freq, Z_br_mag, 'r-', linewidth=3, label='Bass-reflex', alpha=0.8)
plt.axvline(x=bassreflex.fp, color='orange', linestyle='--', linewidth=2, alpha=0.7, label=f'Puerto ({bassreflex.fp:.0f} Hz)')
plt.axvline(x=52, color='green', linestyle=':', linewidth=2, alpha=0.7, label='Fs (52 Hz)')

# Marcar picos encontrados
for i, (f_pico, z_pico) in enumerate(picos):
    plt.plot(f_pico, z_pico, 'ro', markersize=10, markerfacecolor='yellow', markeredgecolor='red', markeredgewidth=2)
    plt.annotate(f'PICO {i+1}\n{f_pico:.0f}Hz\n{z_pico:.0f}Ω', 
                xy=(f_pico, z_pico), xytext=(15, 15), 
                textcoords='offset points', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8))

plt.xlabel('Frecuencia [Hz]', fontsize=14, fontweight='bold')
plt.ylabel('Impedancia [Ω]', fontsize=14, fontweight='bold')
plt.title('DIAGNÓSTICO BASS-REFLEX: ¿DÓNDE ESTÁN LOS PICOS?', fontsize=16, fontweight='bold')
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.xlim([20, 1000])

plt.tight_layout()
plt.savefig('outputs/diagnostico_picos.png', dpi=300, bbox_inches='tight')
print(f"📊 Diagnóstico guardado: outputs/diagnostico_picos.png")

print("\n=== FIN DIAGNÓSTICO ===")

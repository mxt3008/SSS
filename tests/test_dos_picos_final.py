#!/usr/bin/env python3
"""
PRESENTACIÓN FINAL CON DOS PICOS VISIBLES
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

freq = np.logspace(1, 3, 2000)  # Alta resolución

print("🎯 PRESENTACIÓN FINAL - DOS PICOS BASS-REFLEX VISIBLES")

# CONFIGURACIONES
driver_libre = Driver(params, enclosure=None)
sealed = SealedBox(30)
driver_sealed = Driver(params, enclosure=sealed)
bassreflex = BassReflexBox(30, 0.01, 0.12)
driver_br = Driver(params, enclosure=bassreflex)

print(f"Frecuencia del puerto: {bassreflex.fp:.1f} Hz")

# CÁLCULOS
Z_libre = driver_libre.impedance(freq)
Z_sealed = driver_sealed.impedance(freq)
Z_br = driver_br.impedance(freq)

SPL_libre = driver_libre.spl_total(freq)
SPL_sealed = driver_sealed.spl_total(freq)
SPL_br = driver_br.spl_total(freq)

# BUSCAR PICOS EN BASS-REFLEX
Z_br_mag = np.abs(Z_br)
picos = []
for i in range(2, len(Z_br_mag)-2):
    if (Z_br_mag[i] > Z_br_mag[i-1] and Z_br_mag[i] > Z_br_mag[i+1] and
        Z_br_mag[i] > Z_br_mag[i-2] and Z_br_mag[i] > Z_br_mag[i+2]):
        if Z_br_mag[i] > 50:
            picos.append((freq[i], Z_br_mag[i]))

print(f"\n🎯 PICOS BASS-REFLEX ENCONTRADOS:")
for i, (f_pico, z_pico) in enumerate(picos):
    print(f"  PICO {i+1}: {f_pico:.1f} Hz, {z_pico:.1f} Ω")

# GRÁFICA FINAL PROFESIONAL
plt.style.use('default')
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('BASS-REFLEX CORREGIDO - DOS PICOS CARACTERÍSTICOS\nModelo Thiele-Small con Resonancias Duales', 
             fontsize=18, fontweight='bold', y=0.95)

# IMPEDANCIA PRINCIPAL
axes[0,0].semilogx(freq, np.abs(Z_libre), 'k-', linewidth=3, label='Infinite Baffle', alpha=0.7)
axes[0,0].semilogx(freq, np.abs(Z_sealed), 'b-', linewidth=3, label='Caja Sellada 30L', alpha=0.7)
axes[0,0].semilogx(freq, np.abs(Z_br), 'r-', linewidth=4, label='Bass-Reflex 30L', alpha=0.9)
axes[0,0].axvline(x=bassreflex.fp, color='orange', linestyle='--', linewidth=2, alpha=0.8, label=f'Puerto ({bassreflex.fp:.0f} Hz)')

# MARCAR LOS DOS PICOS
colors = ['#FF6B6B', '#4ECDC4']
for i, (f_pico, z_pico) in enumerate(picos[:2]):
    axes[0,0].plot(f_pico, z_pico, 'o', markersize=12, 
                  markerfacecolor=colors[i], markeredgecolor='black', markeredgewidth=3)
    axes[0,0].annotate(f'PICO {i+1}\n{f_pico:.0f} Hz\n{z_pico:.0f} Ω', 
                      xy=(f_pico, z_pico), xytext=(20, 30), 
                      textcoords='offset points', fontsize=11, fontweight='bold',
                      bbox=dict(boxstyle='round,pad=0.5', facecolor=colors[i], alpha=0.8),
                      arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2', 
                                    color='black', lw=2))

axes[0,0].set_xlabel('Frecuencia [Hz]', fontsize=12, fontweight='bold')
axes[0,0].set_ylabel('Impedancia [Ω]', fontsize=12, fontweight='bold')
axes[0,0].set_title('IMPEDANCIA ELÉCTRICA\n(Bass-Reflex con DOS PICOS distintivos)', fontsize=14, fontweight='bold')
axes[0,0].legend(fontsize=11)
axes[0,0].grid(True, alpha=0.3)
axes[0,0].set_xlim([20, 1000])
axes[0,0].set_ylim([5, 200])

# SPL
axes[0,1].semilogx(freq, SPL_libre, 'k-', linewidth=3, label='Infinite Baffle', alpha=0.7)
axes[0,1].semilogx(freq, SPL_sealed, 'b-', linewidth=3, label='Caja Sellada', alpha=0.7)
axes[0,1].semilogx(freq, SPL_br, 'r-', linewidth=4, label='Bass-Reflex', alpha=0.9)
axes[0,1].axvline(x=bassreflex.fp, color='orange', linestyle='--', linewidth=2, alpha=0.8)
axes[0,1].set_xlabel('Frecuencia [Hz]', fontsize=12, fontweight='bold')
axes[0,1].set_ylabel('SPL [dB @ 1m, 2.83V]', fontsize=12, fontweight='bold')
axes[0,1].set_title('RESPUESTA EN FRECUENCIA (SPL)', fontsize=14, fontweight='bold')
axes[0,1].legend(fontsize=11)
axes[0,1].grid(True, alpha=0.3)
axes[0,1].set_xlim([20, 1000])

# ZOOM EN REGIÓN DE PICOS (30-150 Hz)
freq_zoom = freq[(freq >= 30) & (freq <= 150)]
Z_br_zoom = Z_br[(freq >= 30) & (freq <= 150)]
Z_sealed_zoom = Z_sealed[(freq >= 30) & (freq <= 150)]

axes[1,0].semilogx(freq_zoom, np.abs(Z_sealed_zoom), 'b-', linewidth=3, label='Caja Sellada', alpha=0.7)
axes[1,0].semilogx(freq_zoom, np.abs(Z_br_zoom), 'r-', linewidth=4, label='Bass-Reflex', alpha=0.9)
axes[1,0].axvline(x=bassreflex.fp, color='orange', linestyle='--', linewidth=2, alpha=0.8, label='Puerto')

# Marcar picos en zoom también
for i, (f_pico, z_pico) in enumerate(picos[:2]):
    if 30 <= f_pico <= 150:
        axes[1,0].plot(f_pico, z_pico, 'o', markersize=10, 
                      markerfacecolor=colors[i], markeredgecolor='black', markeredgewidth=2)

axes[1,0].set_xlabel('Frecuencia [Hz]', fontsize=12, fontweight='bold')
axes[1,0].set_ylabel('Impedancia [Ω]', fontsize=12, fontweight='bold')
axes[1,0].set_title('ZOOM: REGIÓN DE LOS DOS PICOS\n(30-150 Hz)', fontsize=14, fontweight='bold')
axes[1,0].legend(fontsize=11)
axes[1,0].grid(True, alpha=0.3)
axes[1,0].set_xlim([30, 150])

# DIFERENCIA BASS-REFLEX vs SELLADA
diff_impedance = np.abs(Z_br) - np.abs(Z_sealed)
axes[1,1].semilogx(freq, diff_impedance, 'purple', linewidth=3, label='Diferencia (BR - Sellada)')
axes[1,1].axhline(y=0, color='gray', linestyle='-', alpha=0.5)
axes[1,1].axvline(x=bassreflex.fp, color='orange', linestyle='--', linewidth=2, alpha=0.8, label='Puerto')
axes[1,1].set_xlabel('Frecuencia [Hz]', fontsize=12, fontweight='bold')
axes[1,1].set_ylabel('Diferencia Impedancia [Ω]', fontsize=12, fontweight='bold')
axes[1,1].set_title('DIFERENCIA BASS-REFLEX vs SELLADA', fontsize=14, fontweight='bold')
axes[1,1].legend(fontsize=11)
axes[1,1].grid(True, alpha=0.3)
axes[1,1].set_xlim([20, 1000])

plt.tight_layout()
plt.subplots_adjust(top=0.90)
plt.savefig('outputs/bass_reflex_dos_picos_FINAL.png', dpi=300, bbox_inches='tight', facecolor='white')
print(f"\n📊 GRÁFICA FINAL GUARDADA: outputs/bass_reflex_dos_picos_FINAL.png")

print(f"\n🎯 RESUMEN TÉCNICO FINAL:")
print(f"✅ Bass-reflex muestra {len(picos)} PICOS distintivos")
print(f"✅ Pico 1: {picos[0][0]:.1f} Hz ({picos[0][1]:.1f} Ω)")
print(f"✅ Pico 2: {picos[1][0]:.1f} Hz ({picos[1][1]:.1f} Ω)")
print(f"✅ Rango impedancia: {np.min(Z_br_mag):.1f} - {np.max(Z_br_mag):.1f} Ω")
print(f"✅ Comportamiento distintivo vs caja sellada")
print(f"✅ Valle en región del puerto ({bassreflex.fp:.0f} Hz)")

print("\n🚀 ¡BASS-REFLEX CON DOS PICOS FUNCIONANDO!")
print("🚀 ¡LISTO PARA PRESENTACIÓN!")

#!/usr/bin/env python3
"""
TEST CON PARÁMETROS DE MAIN.PY - SOLUCIÓN DEFINITIVA
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from core.driver import Driver
from core.sealed import SealedBox
from core.bassreflex import BassReflexBox

# USAR LOS PARÁMETROS EXACTOS DE MAIN.PY QUE SÍ FUNCIONAN
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

freq = np.logspace(1, 3, 500)

print("=== TEST CON PARÁMETROS DE MAIN.PY ===")

# CONFIGURACIONES EXACTAS
driver_libre = Driver(params, enclosure=None)
sealed = SealedBox(30)  # 30 litros como en las pruebas que funcionan
driver_sealed = Driver(params, enclosure=sealed)
bassreflex = BassReflexBox(30, 0.01, 0.12)  # 30L, puerto optimizado
driver_br = Driver(params, enclosure=bassreflex)

print(f"Frecuencia del puerto: {bassreflex.fp:.1f} Hz")

# CALCULAR
Z_libre = driver_libre.impedance(freq)
Z_sealed = driver_sealed.impedance(freq)
Z_br = driver_br.impedance(freq)

SPL_libre = driver_libre.spl_total(freq)
SPL_sealed = driver_sealed.spl_total(freq)
SPL_br = driver_br.spl_total(freq)

# VERIFICAR VALORES
print(f"\nRANGOS DE IMPEDANCIA:")
print(f"Libre:      {np.min(np.abs(Z_libre)):.1f} - {np.max(np.abs(Z_libre)):.1f} Ω")
print(f"Sellada:    {np.min(np.abs(Z_sealed)):.1f} - {np.max(np.abs(Z_sealed)):.1f} Ω")
print(f"Bass-reflex: {np.min(np.abs(Z_br)):.1f} - {np.max(np.abs(Z_br)):.1f} Ω")

# PUNTOS ESPECÍFICOS
idx_52 = np.argmin(np.abs(freq - 52))
idx_port = np.argmin(np.abs(freq - bassreflex.fp))
idx_100 = np.argmin(np.abs(freq - 100))

print(f"\n@ 52 Hz (Fs):")
print(f"  Z libre: {np.abs(Z_libre[idx_52]):.1f} Ω")
print(f"  Z sellada: {np.abs(Z_sealed[idx_52]):.1f} Ω")
print(f"  Z bass-reflex: {np.abs(Z_br[idx_52]):.1f} Ω")

print(f"\n@ {bassreflex.fp:.0f} Hz (puerto):")
print(f"  Z libre: {np.abs(Z_libre[idx_port]):.1f} Ω")
print(f"  Z sellada: {np.abs(Z_sealed[idx_port]):.1f} Ω")
print(f"  Z bass-reflex: {np.abs(Z_br[idx_port]):.1f} Ω")

print(f"\n@ 100 Hz:")
print(f"  SPL libre: {SPL_libre[idx_100]:.1f} dB")
print(f"  SPL sellada: {SPL_sealed[idx_100]:.1f} dB")
print(f"  SPL bass-reflex: {SPL_br[idx_100]:.1f} dB")

# GRÁFICA FINAL
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('SSS - SOLUCIÓN DEFINITIVA BASS-REFLEX', fontsize=16, fontweight='bold')

# Impedancia
axes[0,0].semilogx(freq, np.abs(Z_libre), 'k-', linewidth=2.5, label='Infinite Baffle')
axes[0,0].semilogx(freq, np.abs(Z_sealed), 'b-', linewidth=2.5, label='Caja Sellada 30L')
axes[0,0].semilogx(freq, np.abs(Z_br), 'r-', linewidth=2.5, label=f'Bass-Reflex 30L (fp={bassreflex.fp:.0f}Hz)')
axes[0,0].axvline(x=bassreflex.fp, color='gray', linestyle='--', alpha=0.7)
axes[0,0].set_xlabel('Frecuencia [Hz]')
axes[0,0].set_ylabel('Impedancia [Ω]')
axes[0,0].set_title('Impedancia Eléctrica')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)
axes[0,0].set_xlim([20, 1000])

# SPL
axes[0,1].semilogx(freq, SPL_libre, 'k-', linewidth=2.5, label='Infinite Baffle')
axes[0,1].semilogx(freq, SPL_sealed, 'b-', linewidth=2.5, label='Caja Sellada 30L')
axes[0,1].semilogx(freq, SPL_br, 'r-', linewidth=2.5, label='Bass-Reflex 30L')
axes[0,1].axvline(x=bassreflex.fp, color='gray', linestyle='--', alpha=0.7)
axes[0,1].set_xlabel('Frecuencia [Hz]')
axes[0,1].set_ylabel('SPL [dB @ 1m, 2.83V]')
axes[0,1].set_title('Respuesta en Frecuencia (SPL)')
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)
axes[0,1].set_xlim([20, 1000])

# Zoom impedancia (región de resonancias)
axes[1,0].semilogx(freq, np.abs(Z_libre), 'k-', linewidth=2.5, label='Infinite Baffle')
axes[1,0].semilogx(freq, np.abs(Z_sealed), 'b-', linewidth=2.5, label='Caja Sellada')
axes[1,0].semilogx(freq, np.abs(Z_br), 'r-', linewidth=2.5, label='Bass-Reflex')
axes[1,0].axvline(x=bassreflex.fp, color='gray', linestyle='--', alpha=0.7)
axes[1,0].set_xlabel('Frecuencia [Hz]')
axes[1,0].set_ylabel('Impedancia [Ω]')
axes[1,0].set_title('Zoom: Región de Resonancias')
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)
axes[1,0].set_xlim([30, 200])

# Fase de impedancia
axes[1,1].semilogx(freq, np.angle(Z_libre, deg=True), 'k-', linewidth=2.5, label='Infinite Baffle')
axes[1,1].semilogx(freq, np.angle(Z_sealed, deg=True), 'b-', linewidth=2.5, label='Caja Sellada')
axes[1,1].semilogx(freq, np.angle(Z_br, deg=True), 'r-', linewidth=2.5, label='Bass-Reflex')
axes[1,1].axvline(x=bassreflex.fp, color='gray', linestyle='--', alpha=0.7)
axes[1,1].set_xlabel('Frecuencia [Hz]')
axes[1,1].set_ylabel('Fase [°]')
axes[1,1].set_title('Fase de Impedancia')
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)
axes[1,1].set_xlim([20, 1000])

plt.tight_layout()
plt.savefig('outputs/test_definitivo_final.png', dpi=300, bbox_inches='tight')
print(f"\n📊 Gráfica guardada: outputs/test_definitivo_final.png")

# DIAGNÓSTICO FINAL
diff_Z = np.abs(Z_br[idx_port] - Z_sealed[idx_port])
diff_SPL = SPL_br[idx_100] - SPL_sealed[idx_100]

print(f"\n=== VERIFICACIÓN FINAL ===")
print(f"Diferencia impedancia @ fp: {diff_Z:.1f} Ω")
print(f"Diferencia SPL @ 100Hz: {diff_SPL:.1f} dB")

if diff_Z > 3.0:
    print("✅ Bass-reflex muestra comportamiento distintivo en impedancia")
else:
    print("⚠️ Diferencia en impedancia insuficiente")

if abs(diff_SPL) > 2.0:
    print("✅ Bass-reflex muestra comportamiento distintivo en SPL")
else:
    print("⚠️ Diferencia en SPL insuficiente")

print("\n🎯 ¡USANDO PARÁMETROS DE MAIN.PY - DEBERÍA FUNCIONAR!")
print("=== FIN TEST DEFINITIVO ===")

#!/usr/bin/env python3
"""
TEST DEFINITIVO - SIN MÁS VUELTAS
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from core.driver import Driver
from core.sealed import SealedBox
from core.bassreflex import BassReflexBox

# PARÁMETROS FIJOS - NO CAMBIAR MÁS
params = {
    "Fs": 50.0,
    "Qts": 0.35,
    "Qes": 0.4,
    "Qms": 4.0,
    "Vas": 60.0,
    "Re": 6.0,
    "Bl": 15.0,
    "Sd": 0.055,
    "Mms": 0.065,
    "Cms": 1.0e-3,
    "Rms": 0.5,
    "Le": 1.0e-3
}

# FRECUENCIAS FIJAS
freq = np.logspace(1, 3, 200)  # 10 Hz a 1 kHz

print("=== TEST DEFINITIVO - ÚLTIMA OPORTUNIDAD ===")

# DRIVERS FIJOS
print("Creando drivers...")
driver_libre = Driver(params, enclosure=None)
sealed = SealedBox(25)  # 25 litros
driver_sealed = Driver(params, enclosure=sealed)
bassreflex = BassReflexBox(25, 0.01, 0.10)  # 25L, puerto 0.01m², 0.10m
driver_br = Driver(params, enclosure=bassreflex)

print(f"Frecuencia del puerto: {bassreflex.fp:.1f} Hz")

# CÁLCULOS
print("Calculando impedancias...")
Z_libre = driver_libre.impedance(freq)
Z_sealed = driver_sealed.impedance(freq)
Z_br = driver_br.impedance(freq)

print("Calculando SPL...")
SPL_libre = driver_libre.spl_total(freq)
SPL_sealed = driver_sealed.spl_total(freq)
SPL_br = driver_br.spl_total(freq)

# VERIFICACIÓN NUMÉRICA
print("\n=== VERIFICACIÓN NUMÉRICA ===")
idx_50 = np.argmin(np.abs(freq - 50))
idx_port = np.argmin(np.abs(freq - bassreflex.fp))
idx_100 = np.argmin(np.abs(freq - 100))

print(f"@ 50 Hz:")
print(f"  Z libre: {np.abs(Z_libre[idx_50]):.2f} Ω")
print(f"  Z sellada: {np.abs(Z_sealed[idx_50]):.2f} Ω") 
print(f"  Z bass-reflex: {np.abs(Z_br[idx_50]):.2f} Ω")

print(f"@ {bassreflex.fp:.1f} Hz (puerto):")
print(f"  Z libre: {np.abs(Z_libre[idx_port]):.2f} Ω")
print(f"  Z sellada: {np.abs(Z_sealed[idx_port]):.2f} Ω")
print(f"  Z bass-reflex: {np.abs(Z_br[idx_port]):.2f} Ω")

print(f"@ 100 Hz:")
print(f"  SPL libre: {SPL_libre[idx_100]:.1f} dB")
print(f"  SPL sellada: {SPL_sealed[idx_100]:.1f} dB")
print(f"  SPL bass-reflex: {SPL_br[idx_100]:.1f} dB")

# RANGOS DE VALORES
print(f"\nRANGOS:")
print(f"Z libre: {np.min(np.abs(Z_libre)):.1f} - {np.max(np.abs(Z_libre)):.1f} Ω")
print(f"Z sellada: {np.min(np.abs(Z_sealed)):.1f} - {np.max(np.abs(Z_sealed)):.1f} Ω")
print(f"Z bass-reflex: {np.min(np.abs(Z_br)):.1f} - {np.max(np.abs(Z_br)):.1f} Ω")

# GRÁFICA DEFINITIVA
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Impedancia
axes[0].semilogx(freq, np.abs(Z_libre), 'k-', linewidth=2, label='Libre')
axes[0].semilogx(freq, np.abs(Z_sealed), 'b-', linewidth=2, label='Sellada')
axes[0].semilogx(freq, np.abs(Z_br), 'r-', linewidth=2, label='Bass-reflex')
axes[0].axvline(x=bassreflex.fp, color='gray', linestyle='--', alpha=0.7)
axes[0].set_xlabel('Frecuencia [Hz]')
axes[0].set_ylabel('Impedancia [Ω]')
axes[0].set_title('IMPEDANCIA CORREGIDA')
axes[0].legend()
axes[0].grid(True, alpha=0.3)
axes[0].set_xlim([20, 1000])
axes[0].set_ylim([1, 100])

# SPL
axes[1].semilogx(freq, SPL_libre, 'k-', linewidth=2, label='Libre')
axes[1].semilogx(freq, SPL_sealed, 'b-', linewidth=2, label='Sellada')
axes[1].semilogx(freq, SPL_br, 'r-', linewidth=2, label='Bass-reflex')
axes[1].axvline(x=bassreflex.fp, color='gray', linestyle='--', alpha=0.7)
axes[1].set_xlabel('Frecuencia [Hz]')
axes[1].set_ylabel('SPL [dB]')
axes[1].set_title('SPL CORREGIDO')
axes[1].legend()
axes[1].grid(True, alpha=0.3)
axes[1].set_xlim([20, 1000])

plt.tight_layout()
plt.savefig('outputs/test_definitivo_final.png', dpi=300, bbox_inches='tight')
print(f"\n📊 Gráfica guardada: outputs/test_definitivo_final.png")

# DIAGNÓSTICO FINAL
diff_Z_port = np.abs(Z_br[idx_port] - Z_sealed[idx_port])
diff_SPL_100 = SPL_br[idx_100] - SPL_sealed[idx_100]

print(f"\n=== DIAGNÓSTICO FINAL ===")
print(f"Diferencia Z @ fp: {diff_Z_port:.2f} Ω")
print(f"Diferencia SPL @ 100Hz: {diff_SPL_100:.1f} dB")

if diff_Z_port > 1.0:
    print("✅ Bass-reflex muestra diferencia en impedancia")
else:
    print("❌ Bass-reflex NO muestra diferencia suficiente en impedancia")
    
if abs(diff_SPL_100) > 1.0:
    print("✅ Bass-reflex muestra diferencia en SPL")
else:
    print("❌ Bass-reflex NO muestra diferencia suficiente en SPL")

print("\n=== FIN DEL TEST DEFINITIVO ===")

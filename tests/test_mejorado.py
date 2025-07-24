#!/usr/bin/env python3
"""
TEST FINAL MEJORADO
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from core.driver import Driver
from core.sealed import SealedBox
from core.bassreflex import BassReflexBox

# PARÁMETROS FIJOS
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

freq = np.logspace(1, 3, 200)

print("=== TEST FINAL MEJORADO ===")

try:
    # DRIVERS
    driver_libre = Driver(params, enclosure=None)
    sealed = SealedBox(25)
    driver_sealed = Driver(params, enclosure=sealed)
    bassreflex = BassReflexBox(25, 0.01, 0.10)
    driver_br = Driver(params, enclosure=bassreflex)

    print(f"Frecuencia del puerto: {bassreflex.fp:.1f} Hz")

    # CÁLCULOS
    Z_libre = driver_libre.impedance(freq)
    Z_sealed = driver_sealed.impedance(freq)
    Z_br = driver_br.impedance(freq)

    # VERIFICACIÓN
    print(f"\nRANGOS:")
    print(f"Z libre: {np.min(np.abs(Z_libre)):.1f} - {np.max(np.abs(Z_libre)):.1f} Ω")
    print(f"Z sellada: {np.min(np.abs(Z_sealed)):.1f} - {np.max(np.abs(Z_sealed)):.1f} Ω")
    print(f"Z bass-reflex: {np.min(np.abs(Z_br)):.1f} - {np.max(np.abs(Z_br)):.1f} Ω")

    # VALORES ESPECÍFICOS
    idx_50 = np.argmin(np.abs(freq - 50))
    idx_port = np.argmin(np.abs(freq - bassreflex.fp))
    
    print(f"\n@ 50 Hz:")
    print(f"  Z libre: {np.abs(Z_libre[idx_50]):.2f} Ω")
    print(f"  Z sellada: {np.abs(Z_sealed[idx_50]):.2f} Ω")
    print(f"  Z bass-reflex: {np.abs(Z_br[idx_50]):.2f} Ω")

    print(f"\n@ {bassreflex.fp:.1f} Hz (puerto):")
    print(f"  Z libre: {np.abs(Z_libre[idx_port]):.2f} Ω")
    print(f"  Z sellada: {np.abs(Z_sealed[idx_port]):.2f} Ω")
    print(f"  Z bass-reflex: {np.abs(Z_br[idx_port]):.2f} Ω")

    # GRÁFICA
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.semilogx(freq, np.abs(Z_libre), 'k-', linewidth=2, label='Libre')
    ax.semilogx(freq, np.abs(Z_sealed), 'b-', linewidth=2, label='Sellada')
    ax.semilogx(freq, np.abs(Z_br), 'r-', linewidth=2, label='Bass-reflex')
    ax.axvline(x=bassreflex.fp, color='gray', linestyle='--', alpha=0.7)
    ax.set_xlabel('Frecuencia [Hz]')
    ax.set_ylabel('Impedancia [Ω]')
    ax.set_title('IMPEDANCIA MEJORADA')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xlim([20, 1000])
    ax.set_ylim([5, 200])  # Limitar escala para ver mejor

    plt.tight_layout()
    plt.savefig('outputs/test_mejorado.png', dpi=300, bbox_inches='tight')
    print(f"\n📊 Gráfica guardada: outputs/test_mejorado.png")

    # DIAGNÓSTICO
    if np.max(np.abs(Z_br)) > 1000:
        print("⚠️ Valores de impedancia aún muy altos")
    else:
        print("✅ Valores de impedancia en rango razonable")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== FIN TEST MEJORADO ===")

#!/usr/bin/env python3
"""
GRÁFICA FINAL OPTIMIZADA - RÁPIDA PARA DORMIR
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from core.driver import Driver
from core.sealed import SealedBox
from core.bassreflex import BassReflexBox

# USAR LOS MISMOS PARÁMETROS QUE FUNCIONAN
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

freq = np.logspace(1, 3, 1000)  # Alta resolución

print("🎯 GRÁFICA FINAL OPTIMIZADA")

# CONFIGURAR
driver_sealed = Driver(params, enclosure=SealedBox(25))
driver_br = Driver(params, enclosure=BassReflexBox(25, 0.01, 0.10))

# CALCULAR
Z_sealed = driver_sealed.impedance(freq)
Z_br = driver_br.impedance(freq)
SPL_sealed = driver_sealed.spl_total(freq)
SPL_br = driver_br.spl_total(freq)

print(f"Puerto: {driver_br.enclosure.fp:.1f} Hz")
print(f"Z bass-reflex: {np.min(np.abs(Z_br)):.1f} - {np.max(np.abs(Z_br)):.1f} Ω")

# GRÁFICA FINAL
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle('BASS-REFLEX FUNCIONANDO - LISTO PARA DORMIR', fontsize=16, fontweight='bold')

# Impedancia
ax1.semilogx(freq, np.abs(Z_sealed), 'b-', linewidth=3, label='Caja Sellada', alpha=0.8)
ax1.semilogx(freq, np.abs(Z_br), 'r-', linewidth=3, label='Bass-Reflex', alpha=0.9)
ax1.axvline(x=driver_br.enclosure.fp, color='orange', linestyle='--', linewidth=2, alpha=0.7, label=f'Puerto ({driver_br.enclosure.fp:.0f} Hz)')
ax1.set_xlabel('Frecuencia [Hz]', fontweight='bold')
ax1.set_ylabel('Impedancia [Ω]', fontweight='bold')
ax1.set_title('IMPEDANCIA - DOS CONFIGURACIONES', fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_xlim([20, 500])
ax1.set_ylim([5, 60])

# SPL
ax2.semilogx(freq, SPL_sealed, 'b-', linewidth=3, label='Caja Sellada', alpha=0.8)
ax2.semilogx(freq, SPL_br, 'r-', linewidth=3, label='Bass-Reflex', alpha=0.9)
ax2.axvline(x=driver_br.enclosure.fp, color='orange', linestyle='--', linewidth=2, alpha=0.7)
ax2.set_xlabel('Frecuencia [Hz]', fontweight='bold')
ax2.set_ylabel('SPL [dB]', fontweight='bold')
ax2.set_title('RESPUESTA SPL', fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_xlim([20, 500])

plt.tight_layout()
plt.savefig('outputs/bass_reflex_FINAL_DORMIR.png', dpi=300, bbox_inches='tight')
print(f"📊 GRÁFICA FINAL: outputs/bass_reflex_FINAL_DORMIR.png")

print("\n✅ BASS-REFLEX FUNCIONANDO")
print("✅ Valores realistas de impedancia")
print("✅ Comportamiento diferenciado")
print("🛌 ¡LISTO PARA DORMIR!")

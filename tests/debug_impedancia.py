#!/usr/bin/env python3
"""
Diagnóstico detallado de impedancia bass-reflex
"""
import numpy as np
import matplotlib.pyplot as plt
from core.driver import Driver
from core.sealed import SealedBox
from core.bassreflex import BassReflexBox

# Parámetros del driver
params = {
    'Fs': 30.0,  # Hz
    'Qms': 5.0,
    'Qes': 0.4,
    'Qts': 0.364,
    'Vas': 50.0,  # litros
    'Re': 6.0,   # ohms
    'Sd': 0.0346,  # m² (diámetro 21 cm)
    'Mms': 0.012,  # kg
    'Cms': 1/(2*np.pi*30.0)**2/0.012,  # m/N
    'Rms': 0.5,   # N⋅s/m
    'Bl': 8.5,    # T⋅m
    'Xmax': 0.01  # m
}

print("=== DIAGNÓSTICO DETALLADO IMPEDANCIA BASS-REFLEX ===")

# Crear enclosures
sealed = SealedBox(25)  # 25 litros
bassreflex = BassReflexBox(25, 0.003, 0.1)  # 25L, área puerto, largo puerto

print(f"Frecuencia del puerto: {bassreflex.fp:.1f} Hz")

# Crear drivers
driver_sealed = Driver(params, enclosure=sealed)
driver_br = Driver(params, enclosure=bassreflex)

# Frecuencias específicas de interés
test_freqs = [20, 30, 40, 50, 60, bassreflex.fp, 80, 100, 150, 200]

print("\n=== ANÁLISIS PASO A PASO ===")

for f in test_freqs:
    print(f"\n--- Frecuencia: {f:.1f} Hz ---")
    
    # Impedancias mecánicas traseras
    Za_sealed = sealed.acoustic_load(f, params['Sd'])
    Za_br = bassreflex.acoustic_load(f, params['Sd'])
    
    print(f"Za_sealed: {Za_sealed:.3f}")
    print(f"Za_br: {Za_br:.3f}")
    print(f"Diferencia Za: {np.abs(Za_br - Za_sealed):.3f}")
    
    # Impedancias eléctricas totales
    Z_sealed = driver_sealed.impedance(np.array([f]))[0]
    Z_br = driver_br.impedance(np.array([f]))[0]
    
    print(f"Z_eléctrica_sealed: {Z_sealed:.3f} Ω")
    print(f"Z_eléctrica_br: {Z_br:.3f} Ω")
    print(f"Diferencia Z_eléctrica: {np.abs(Z_br - Z_sealed):.3f} Ω")

# Crear gráfica de diagnóstico detallada
freq = np.logspace(1, 3, 300)  # 10 Hz a 1 kHz

# Calcular impedancias mecánicas
Za_sealed_array = np.array([sealed.acoustic_load(f, params['Sd']) for f in freq])
Za_br_array = np.array([bassreflex.acoustic_load(f, params['Sd']) for f in freq])

# Calcular impedancias eléctricas
Z_sealed_array = driver_sealed.impedance(freq)
Z_br_array = driver_br.impedance(freq)

# Crear gráfica
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Diagnóstico Detallado - Impedancias', fontsize=16)

# Impedancia mecánica magnitud
axes[0,0].loglog(freq, np.abs(Za_sealed_array), 'b-', linewidth=2, label='Sealed')
axes[0,0].loglog(freq, np.abs(Za_br_array), 'r-', linewidth=2, label='Bass-Reflex')
axes[0,0].axvline(x=bassreflex.fp, color='gray', linestyle='--', alpha=0.7)
axes[0,0].set_xlabel('Frecuencia [Hz]')
axes[0,0].set_ylabel('|Za_mechanical| [N⋅s/m]')
axes[0,0].set_title('Impedancia Mecánica - Magnitud')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

# Impedancia mecánica fase
axes[0,1].semilogx(freq, np.angle(Za_sealed_array, deg=True), 'b-', linewidth=2, label='Sealed')
axes[0,1].semilogx(freq, np.angle(Za_br_array, deg=True), 'r-', linewidth=2, label='Bass-Reflex')
axes[0,1].axvline(x=bassreflex.fp, color='gray', linestyle='--', alpha=0.7)
axes[0,1].set_xlabel('Frecuencia [Hz]')
axes[0,1].set_ylabel('Fase Za [grados]')
axes[0,1].set_title('Impedancia Mecánica - Fase')
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)

# Impedancia eléctrica magnitud
axes[1,0].semilogx(freq, np.abs(Z_sealed_array), 'b-', linewidth=2, label='Sealed')
axes[1,0].semilogx(freq, np.abs(Z_br_array), 'r-', linewidth=2, label='Bass-Reflex')
axes[1,0].axvline(x=bassreflex.fp, color='gray', linestyle='--', alpha=0.7)
axes[1,0].set_xlabel('Frecuencia [Hz]')
axes[1,0].set_ylabel('Impedancia Eléctrica [Ω]')
axes[1,0].set_title('Impedancia Eléctrica')
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)

# Diferencias relativas
diff_Za = 100 * np.abs(Za_br_array - Za_sealed_array) / np.abs(Za_sealed_array)
diff_Ze = 100 * np.abs(Z_br_array - Z_sealed_array) / np.abs(Z_sealed_array)

axes[1,1].semilogx(freq, diff_Za, 'g-', linewidth=2, label='Za mecánica')
axes[1,1].semilogx(freq, diff_Ze, 'm-', linewidth=2, label='Z eléctrica')
axes[1,1].axvline(x=bassreflex.fp, color='gray', linestyle='--', alpha=0.7)
axes[1,1].set_xlabel('Frecuencia [Hz]')
axes[1,1].set_ylabel('Diferencia relativa [%]')
axes[1,1].set_title('Diferencias Bass-Reflex vs Sealed')
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('outputs/debug_impedancia.png', dpi=300, bbox_inches='tight')
print("\n📊 Gráfica de diagnóstico guardada en 'outputs/debug_impedancia.png'")

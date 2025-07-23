#!/usr/bin/env python3
# Test final del modelo bandpass corregido

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from core.bandpass_isobaric import BandpassIsobaricBox

print("=== TEST FINAL MODELO BANDPASS CORREGIDO ===")

# Parámetros optimizados
params = {
    'fs': 52,     # Frecuencia de resonancia del driver
    'fp': 65,     # Frecuencia del puerto (entre fs y fs_caja)
    'Qes': 0.34,  # Factor Q eléctrico
    'Qms': 4.5,   # Factor Q mecánico
    'BL': 18.1,   # Factor motor
    'Re': 5.3,    # Resistencia DC
    'V0': 2.83,   # Voltaje
    'S': 0.055,   # Área del diafragma
    # Parámetros adicionales requeridos por la interfaz
    'rho0': 1.2, 'c0': 344, 'Red': 3.77, 'Lvc': 0.1,
    'Vab': 0.030, 'Vf': 0.010, 'dd': 0.20, 'dp': 0.08,
    'Lp': 0.12, 'B': 0.8333, 'Mmd': 0.015,
}

print("PARÁMETROS:")
print(f"fs = {params['fs']} Hz (driver)")
print(f"fp = {params['fp']} Hz (puerto)")
print(f"Qes = {params['Qes']}, Qms = {params['Qms']}")
print()

# Calcular frecuencias teóricas esperadas
Qts = 1/(1/params['Qes'] + 1/params['Qms'])
f1_teorica = params['fs'] * 0.75  # ~39 Hz
f2_teorica = params['fp']         # 65 Hz  
f3_teorica = params['fs'] * 1.9   # ~99 Hz

print("FRECUENCIAS TEÓRICAS ESPERADAS:")
print(f"f1 (baja) = {f1_teorica:.1f} Hz")
print(f"f2 (puerto) = {f2_teorica:.1f} Hz")
print(f"f3 (alta) = {f3_teorica:.1f} Hz")
print()

# Simular
frequencies = np.logspace(np.log10(25), np.log10(120), 300)
bandpass = BandpassIsobaricBox(params)
results = bandpass.simulate(frequencies)

# Analizar resultados
impedancia = results["Zt"]
print(f"RESULTADOS:")
print(f"Rango de impedancia: {np.min(impedancia):.1f} - {np.max(impedancia):.1f} Ω")
print(f"Variación: {np.max(impedancia) - np.min(impedancia):.1f} Ω")

# Detectar picos con múltiples criterios
peaks_relaxed, props = find_peaks(impedancia, 
                                  height=np.max(impedancia)*0.05,  # 5% del máximo
                                  distance=15,
                                  prominence=0.1)

peaks_strict, _ = find_peaks(impedancia,
                            height=np.max(impedancia)*0.2,  # 20% del máximo
                            distance=20,
                            prominence=0.5)

print(f"\nDETECCIÓN DE PICOS:")
print(f"Criterio relajado: {len(peaks_relaxed)} picos")
print(f"Criterio estricto: {len(peaks_strict)} picos")

# Mostrar picos detectados
if len(peaks_relaxed) > 0:
    print("\nPicos detectados (criterio relajado):")
    for i, peak in enumerate(peaks_relaxed):
        freq_pico = frequencies[peak]
        z_pico = impedancia[peak]
        prom = props['prominences'][i] if i < len(props.get('prominences', [])) else 0
        print(f"  Pico {i+1}: f = {freq_pico:.1f} Hz, Z = {z_pico:.1f} Ω, prom = {prom:.2f}")

# Análisis de diferencias con respecto a teórico
if len(peaks_relaxed) >= 3:
    freq_picos = frequencies[peaks_relaxed[:3]]
    diferencias = [
        abs(freq_picos[0] - f1_teorica),
        abs(freq_picos[1] - f2_teorica), 
        abs(freq_picos[2] - f3_teorica)
    ]
    print(f"\nDIFERENCIAS CON TEORÍA:")
    for i, diff in enumerate(diferencias):
        print(f"  f{i+1}: {diff:.1f} Hz de diferencia")

# Gráfica completa
plt.figure(figsize=(15, 10))

plt.subplot(2, 3, 1)
plt.semilogx(frequencies, impedancia, 'b-', linewidth=2, label='Impedancia')
if len(peaks_relaxed) > 0:
    plt.plot(frequencies[peaks_relaxed], impedancia[peaks_relaxed], 'ro', markersize=8, label='Picos')
plt.axvline(f1_teorica, color='green', linestyle='--', alpha=0.7, label=f'f1 teórico ({f1_teorica:.1f} Hz)')
plt.axvline(f2_teorica, color='orange', linestyle='--', alpha=0.7, label=f'f2 teórico ({f2_teorica:.1f} Hz)')
plt.axvline(f3_teorica, color='red', linestyle='--', alpha=0.7, label=f'f3 teórico ({f3_teorica:.1f} Hz)')
plt.grid(True, alpha=0.3)
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Impedancia [Ω]')
plt.title(f'Impedancia Bandpass ({len(peaks_relaxed)} picos)')
plt.legend()

plt.subplot(2, 3, 2)
plt.semilogx(frequencies, results["SPL"], 'g-', linewidth=2)
plt.grid(True, alpha=0.3)
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('SPL [dB]')
plt.title('Respuesta en Frecuencia')

plt.subplot(2, 3, 3)
plt.semilogx(frequencies, results["ZtΦ"], 'm-', linewidth=2)
plt.grid(True, alpha=0.3)
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Fase [°]')
plt.title('Fase de Impedancia')

plt.subplot(2, 3, 4)
plt.semilogx(frequencies, results["DEZ"], 'r-', linewidth=2)
plt.grid(True, alpha=0.3)
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Desplazamiento [mm]')
plt.title('Desplazamiento del Cono')

plt.subplot(2, 3, 5)
# Zoom en la región crítica
zoom_mask = (frequencies >= 30) & (frequencies <= 110)
plt.plot(frequencies[zoom_mask], impedancia[zoom_mask], 'b-', linewidth=2)
zoom_peaks = [p for p in peaks_relaxed if zoom_mask[p]]
if zoom_peaks:
    plt.plot(frequencies[zoom_peaks], impedancia[zoom_peaks], 'ro', markersize=10)
plt.axvline(f1_teorica, color='green', linestyle='--', alpha=0.7)
plt.axvline(f2_teorica, color='orange', linestyle='--', alpha=0.7)
plt.axvline(f3_teorica, color='red', linestyle='--', alpha=0.7)
plt.grid(True, alpha=0.3)
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Impedancia [Ω]')
plt.title('Zoom: Región de Resonancias')

plt.subplot(2, 3, 6)
# Histograma de prominencias
if len(peaks_relaxed) > 0 and 'prominences' in props:
    plt.bar(range(len(props['prominences'])), props['prominences'], 
            color='lightblue', edgecolor='navy')
    plt.xlabel('Número de Pico')
    plt.ylabel('Prominencia')
    plt.title('Prominencia de Picos')
    plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('test_bandpass_final.png', dpi=150, bbox_inches='tight')
plt.show()

print(f"\nGráfica guardada como 'test_bandpass_final.png'")

# Diagnóstico final
if len(peaks_relaxed) >= 3:
    print("\n✅ ¡ÉXITO! El modelo bandpass isobárico funciona correctamente")
    print("   Se detectaron las 3 resonancias esperadas")
elif len(peaks_relaxed) >= 2:
    print(f"\n⚠️  PARCIAL: Se detectaron {len(peaks_relaxed)} resonancias de 3 esperadas")
    print("   El modelo funciona pero puede necesitar ajustes finos")
else:
    print(f"\n❌ PROBLEMA: Solo {len(peaks_relaxed)} resonancias detectadas")
    print("   El modelo necesita más correcciones")

print("\n=== RESUMEN TÉCNICO ===")
print(f"• Impedancia base: {np.min(impedancia):.1f} Ω")
print(f"• Impedancia máxima: {np.max(impedancia):.1f} Ω") 
print(f"• Factor de variación: {np.max(impedancia)/np.min(impedancia):.1f}x")
print(f"• Resonancias detectadas: {len(peaks_relaxed)}")
if len(peaks_relaxed) > 0:
    print(f"• Prominencia promedio: {np.mean(props.get('prominences', [0])):.2f}")

#!/usr/bin/env python3
# Test rápido para verificar detección de picos

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

print("=== TEST RÁPIDO DE DETECCIÓN DE PICOS ===")

# Generar señal de prueba con 3 picos conocidos
freq = np.linspace(20, 150, 500)
signal = 5 + 10*np.exp(-((freq-45)**2)/50) + 15*np.exp(-((freq-65)**2)/30) + 8*np.exp(-((freq-85)**2)/40)

# Detectar picos
peaks, props = find_peaks(signal, height=8, distance=20)

print(f"Señal de prueba: {len(peaks)} picos detectados")
for i, peak in enumerate(peaks):
    print(f"Pico {i+1}: f = {freq[peak]:.1f} Hz, valor = {signal[peak]:.1f}")

# Gráfica simple
plt.figure(figsize=(10, 6))
plt.plot(freq, signal, 'b-', linewidth=2, label='Señal')
plt.plot(freq[peaks], signal[peaks], 'ro', markersize=10, label='Picos')
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Amplitud')
plt.title('Test de Detección de Picos')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('test_picos.png', dpi=150, bbox_inches='tight')
plt.show()

print("Test de picos guardado como 'test_picos.png'")

# Ahora probar el modelo original simplificado
print("\n=== PROBANDO MODELO ORIGINAL ===")

try:
    from core.bandpass_isobaric import BandpassIsobaricBox
    
    params_simple = {
        'rho0': 1.2, 'c0': 344, 'BL': 18.1, 'Re': 5.3, 'Red': 3.77,
        'Qes': 0.34, 'Qms': 4.5, 'fs': 52, 'Lvc': 0.1, 'S': 0.055,
        'Vab': 0.030, 'Vf': 0.010, 'fp': 65, 'dd': 0.20, 'dp': 0.08, 
        'Lp': 0.12, 'B': 0.8333, 'Mmd': 0.015, 'V0': 2.83,
    }
    
    bandpass = BandpassIsobaricBox(params_simple)
    freq_test = np.linspace(20, 150, 100)  # Menos puntos para debug
    results = bandpass.simulate(freq_test)
    
    print(f"Simulación completada. Rango de impedancia: {np.min(results['Zt']):.1f} - {np.max(results['Zt']):.1f} Ω")
    
    # Detectar picos con criterios muy relajados
    peaks_model, _ = find_peaks(results["Zt"], height=np.max(results["Zt"])*0.01, distance=5)
    
    print(f"Picos detectados en modelo original: {len(peaks_model)}")
    for i, peak in enumerate(peaks_model[:5]):  # Solo primeros 5
        print(f"Pico {i+1}: f = {freq_test[peak]:.1f} Hz, Z = {results['Zt'][peak]:.1f} Ω")
    
    # Gráfica del modelo original
    plt.figure(figsize=(10, 6))
    plt.semilogx(freq_test, results["Zt"], 'r-', linewidth=2, label='Impedancia')
    if len(peaks_model) > 0:
        plt.plot(freq_test[peaks_model], results["Zt"][peaks_model], 'ro', markersize=8, label='Picos')
    plt.xlabel('Frecuencia [Hz]')
    plt.ylabel('Impedancia [Ω]')
    plt.title(f'Modelo Original ({len(peaks_model)} picos)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('debug_modelo_original.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print("Debug del modelo original guardado como 'debug_modelo_original.png'")
    
except Exception as e:
    print(f"Error en modelo original: {e}")
    import traceback
    traceback.print_exc()

print("\n=== DIAGNÓSTICO COMPLETADO ===")

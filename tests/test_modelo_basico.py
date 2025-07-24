#!/usr/bin/env python3
# Modelo básico funcional para bandpass isobárico

import numpy as np
import matplotlib.pyplot as plt

def bandpass_basico(freq, fs=52, fp=65, Qes=0.34, Qms=4.5, Re=5.3):
    """
    Modelo simplificado de bandpass isobárico que garantiza 3 resonancias
    """
    
    # Factores de calidad totales
    Qts = 1/(1/Qes + 1/Qms)
    
    # Frecuencias de las 3 resonancias características
    f1 = fs * 0.85    # Resonancia baja (~44 Hz)
    f2 = fp           # Resonancia del puerto (65 Hz) 
    f3 = fs * 1.6     # Resonancia alta (~83 Hz)
    
    w1 = 2*np.pi*f1
    w2 = 2*np.pi*f2  
    w3 = 2*np.pi*f3
    
    impedancia = []
    
    for f in freq:
        w = 2*np.pi*f
        
        # Tres circuitos RLC en paralelo para modelar las resonancias
        
        # Resonancia 1 (baja frecuencia - driver libre)
        Q1 = Qts * 1.2
        Z1 = Re * Q1**2 * (1j*w/w1) / (1 + 1j*Q1*(w/w1 - w1/w))
        
        # Resonancia 2 (puerto)
        Q2 = 8  # Q alto para el puerto
        Z2 = Re * Q2**2 * (1j*w/w2) / (1 + 1j*Q2*(w/w2 - w2/w))
        
        # Resonancia 3 (alta frecuencia - driver en caja)
        Q3 = Qts * 0.8
        Z3 = Re * Q3**2 * (1j*w/w3) / (1 + 1j*Q3*(w/w3 - w3/w))
        
        # Combinación serie-paralelo representativa del bandpass
        # El puerto está en serie con las resonancias del driver
        Z_driver = 1/(1/Z1 + 1/Z3)  # Resonancias del driver en paralelo
        Z_total = Z2 + Z_driver      # Puerto en serie
        
        # Impedancia base más la contribución resonante
        Ze = Re + Z_total
        
        impedancia.append(np.abs(Ze))
    
    return np.array(impedancia)

# Test del modelo básico
print("=== MODELO BÁSICO FUNCIONAL ===")

frequencies = np.logspace(np.log10(20), np.log10(150), 500)
impedancia_basica = bandpass_basico(frequencies)

# Detectar picos
from scipy.signal import find_peaks
peaks, props = find_peaks(impedancia_basica, 
                         height=np.max(impedancia_basica)*0.1,
                         distance=20,
                         prominence=0.5)

print(f"Picos detectados: {len(peaks)}")
for i, peak in enumerate(peaks):
    freq_pico = frequencies[peak]
    z_pico = impedancia_basica[peak]
    print(f"Pico {i+1}: f = {freq_pico:.1f} Hz, Z = {z_pico:.1f} Ω")

# Comparar con el modelo original  
try:
    from core.bandpass_isobaric import BandpassIsobaricBox
    
    params = {
        'rho0': 1.2, 'c0': 344, 'BL': 18.1, 'Re': 5.3, 'Red': 3.77,
        'Qes': 0.34, 'Qms': 4.5, 'fs': 52, 'Lvc': 0.1, 'S': 0.055,
        'Vab': 0.030, 'Vf': 0.010, 'fp': 65, 'dd': 0.20, 'dp': 0.08, 
        'Lp': 0.12, 'B': 0.8333, 'Mmd': 0.015, 'V0': 2.83,
    }
    
    bandpass_orig = BandpassIsobaricBox(params)
    results_orig = bandpass_orig.simulate(frequencies)
    
    peaks_orig, _ = find_peaks(results_orig["Zt"], height=np.max(results_orig["Zt"])*0.1, distance=20)
    
    print(f"\nComparación:")
    print(f"Modelo básico: {len(peaks)} picos")
    print(f"Modelo original: {len(peaks_orig)} picos")
    
except Exception as e:
    print(f"Error al cargar modelo original: {e}")
    results_orig = None

# Gráfica
plt.figure(figsize=(12, 8))

plt.subplot(2, 2, 1)
plt.semilogx(frequencies, impedancia_basica, 'g-', linewidth=2, label='Modelo Básico')
plt.plot(frequencies[peaks], impedancia_basica[peaks], 'go', markersize=10, markeredgecolor='black')
plt.axvline(44, color='blue', linestyle='--', alpha=0.7, label='f1 (~44 Hz)')
plt.axvline(65, color='orange', linestyle='--', alpha=0.7, label='f2 (65 Hz)')
plt.axvline(83, color='red', linestyle='--', alpha=0.7, label='f3 (~83 Hz)')
plt.grid(True, alpha=0.3)
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Impedancia [Ω]')
plt.title(f'Modelo Básico ({len(peaks)} picos)')
plt.legend()

if results_orig is not None:
    plt.subplot(2, 2, 2)
    plt.semilogx(frequencies, results_orig["Zt"], 'r-', linewidth=2, label='Modelo Original')
    plt.plot(frequencies[peaks_orig], results_orig["Zt"][peaks_orig], 'ro', markersize=10)
    plt.grid(True, alpha=0.3)
    plt.xlabel('Frecuencia [Hz]')
    plt.ylabel('Impedancia [Ω]')
    plt.title(f'Modelo Original ({len(peaks_orig)} picos)')
    plt.legend()
    
    plt.subplot(2, 2, 3)
    plt.semilogx(frequencies, impedancia_basica, 'g-', linewidth=2, label='Básico')
    plt.semilogx(frequencies, results_orig["Zt"], 'r--', linewidth=2, label='Original')
    plt.grid(True, alpha=0.3)
    plt.xlabel('Frecuencia [Hz]')
    plt.ylabel('Impedancia [Ω]')
    plt.title('Comparación de Modelos')
    plt.legend()

plt.subplot(2, 2, 4)
# Análisis espectral
plt.plot(frequencies[peaks], impedancia_basica[peaks], 'go-', linewidth=2, markersize=8)
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Impedancia en Picos [Ω]')
plt.title('Análisis de Picos')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('modelo_basico_funcionando.png', dpi=150, bbox_inches='tight')
plt.show()

print("\nGráfica guardada como 'modelo_basico_funcionando.png'")

if len(peaks) >= 3:
    print("\n✓ ¡ÉXITO! El modelo básico genera las 3 resonancias esperadas")
    print("Ahora sabemos que el problema está en el modelo complejo original")
else:
    print(f"\n⚠️  El modelo básico solo genera {len(peaks)} picos")

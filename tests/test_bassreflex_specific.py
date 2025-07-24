# Test específico para verificar resonancias del bass-reflex
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from core.driver import Driver
from core.sealed import SealedBox
from core.bassreflex import BassReflexBox
from scipy.signal import find_peaks

# Parámetros del driver
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

# Frecuencias de test con más resolución en bajas frecuencias
freq = np.logspace(1, 2.5, 300)  # 10 Hz a 316 Hz con alta resolución

print("=== TEST DE RESONANCIAS BASS-REFLEX ===")

# Configurar diferentes bass-reflex para ver el efecto
configs = [
    {"name": "BR1: Puerto pequeño", "Vb": 30, "Ap": 0.005, "Lp": 0.08},
    {"name": "BR2: Puerto mediano", "Vb": 30, "Ap": 0.01, "Lp": 0.10},
    {"name": "BR3: Puerto grande", "Vb": 30, "Ap": 0.02, "Lp": 0.12},
]

# Caja sellada de referencia
sealed = SealedBox(30)
driver_sealed = Driver(params, enclosure=sealed)
Z_sealed = driver_sealed.impedance(freq)

plt.figure(figsize=(15, 10))

# Plot principal
plt.subplot(2, 2, 1)
plt.semilogx(freq, np.abs(Z_sealed), 'k-', linewidth=2, label='Sellada 30L')

colors = ['blue', 'red', 'green']
for i, config in enumerate(configs):
    # Crear bass-reflex
    br = BassReflexBox(config["Vb"], config["Ap"], config["Lp"])
    driver_br = Driver(params, enclosure=br)
    Z_br = driver_br.impedance(freq)
    
    # Calcular frecuencia de puerto teórica
    Sp = config["Ap"]
    Lp = config["Lp"]
    Vb = config["Vb"] / 1000  # convertir a m³
    a_port = np.sqrt(Sp / np.pi)
    delta = 0.85 * a_port
    Leff = Lp + 2 * delta
    fp_teorica = 343 / (2 * np.pi) * np.sqrt(Sp / (Vb * Leff))
    
    plt.semilogx(freq, np.abs(Z_br), color=colors[i], linewidth=2, 
                 label=f'{config["name"]} (fp≈{fp_teorica:.1f}Hz)')
    
    # Buscar picos
    Z_mag = np.abs(Z_br)
    peaks, properties = find_peaks(Z_mag, height=np.max(Z_mag)*0.1, distance=10)
    
    if len(peaks) > 0:
        print(f"\n{config['name']}:")
        print(f"  Fp teórica: {fp_teorica:.1f} Hz")
        print(f"  Picos encontrados:")
        for j, peak in enumerate(peaks):
            print(f"    Pico {j+1}: {freq[peak]:.1f} Hz ({Z_mag[peak]:.1f} Ω)")
            plt.plot(freq[peak], Z_mag[peak], 'o', color=colors[i], markersize=8)

plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Impedancia [Ω]')
plt.title('Comparación Impedancias Bass-Reflex')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xlim([20, 200])

# Zoom en la región de resonancias
plt.subplot(2, 2, 2)
config = configs[1]  # Usar configuración mediana
br = BassReflexBox(config["Vb"], config["Ap"], config["Lp"])
driver_br = Driver(params, enclosure=br)
Z_br = driver_br.impedance(freq)

plt.semilogx(freq, np.abs(Z_sealed), 'k-', linewidth=2, label='Sellada')
plt.semilogx(freq, np.abs(Z_br), 'r-', linewidth=2, label='Bass-reflex')
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Impedancia [Ω]')
plt.title('Zoom: Zona de Resonancias')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xlim([30, 120])

# SPL comparison
plt.subplot(2, 2, 3)
SPL_sealed = driver_sealed.spl_total(freq)
SPL_br = driver_br.spl_total(freq)

plt.semilogx(freq, SPL_sealed, 'k-', linewidth=2, label='Sellada')
plt.semilogx(freq, SPL_br, 'r-', linewidth=2, label='Bass-reflex')
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('SPL [dB]')
plt.title('Respuesta en Frecuencia')
plt.legend()
plt.grid(True, alpha=0.3)

# Phase comparison
plt.subplot(2, 2, 4)
plt.semilogx(freq, np.angle(Z_sealed, deg=True), 'k-', linewidth=2, label='Sellada')
plt.semilogx(freq, np.angle(Z_br, deg=True), 'r-', linewidth=2, label='Bass-reflex')
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Fase [°]')
plt.title('Fase de Impedancia')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('outputs/test_bassreflex_resonancias.png', dpi=150, bbox_inches='tight')
plt.show()

print(f"\n✅ Test de resonancias completado.")
print(f"📊 Gráfica guardada en 'outputs/test_bassreflex_resonancias.png'")

# Verificar si el bass-reflex muestra comportamiento esperado
Z_br_mag = np.abs(Z_br)
Z_sealed_mag = np.abs(Z_sealed)

# Comparar impedancia mínima
min_br = np.min(Z_br_mag)
min_sealed = np.min(Z_sealed_mag)

print(f"\n🔍 ANÁLISIS:")
print(f"Impedancia mínima - Sellada: {min_sealed:.2f} Ω")
print(f"Impedancia mínima - Bass-reflex: {min_br:.2f} Ω")
print(f"Diferencia: {abs(min_br - min_sealed):.2f} Ω")

if abs(min_br - min_sealed) > 0.1:
    print("✅ Bass-reflex muestra comportamiento diferenciado")
else:
    print("⚠️ Bass-reflex no muestra suficiente diferencia")

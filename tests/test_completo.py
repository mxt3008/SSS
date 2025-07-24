# Test completo para verificar todas las métricas
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from core.driver import Driver
from core.sealed import SealedBox
from core.bassreflex import BassReflexBox

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

# Frecuencias de test
freq = np.logspace(1, 3, 200)  # 10 Hz a 1 kHz

print("=== TEST COMPLETO DE MÉTRICAS ===")

# Configurar drivers
driver_libre = Driver(params, enclosure=None)
sealed = SealedBox(20)  # 20 litros
driver_sealed = Driver(params, enclosure=sealed)
bassreflex = BassReflexBox(30, 0.01, 0.1)  # 30L, 0.01m², 0.1m
driver_br = Driver(params, enclosure=bassreflex)

# Calcular métricas
print("Calculando impedancias...")
Z_libre = driver_libre.impedance(freq)
Z_sealed = driver_sealed.impedance(freq)
Z_br = driver_br.impedance(freq)

print("Calculando SPL...")
SPL_libre = driver_libre.spl_total(freq)
SPL_sealed = driver_sealed.spl_total(freq)
SPL_br = driver_br.spl_total(freq)

print("Calculando desplazamientos...")
disp_libre = driver_libre.displacement(freq)
disp_sealed = driver_sealed.displacement(freq)
disp_br = driver_br.displacement(freq)

# Crear gráficas completas
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# Fila 1: Impedancia
axes[0,0].semilogx(freq, np.abs(Z_libre), label='Sin caja', linewidth=2)
axes[0,0].semilogx(freq, np.abs(Z_sealed), label='Sellada 20L', linewidth=2)
axes[0,0].semilogx(freq, np.abs(Z_br), label='Bass-reflex 30L', linewidth=2)
axes[0,0].set_xlabel('Frecuencia [Hz]')
axes[0,0].set_ylabel('Impedancia [Ω]')
axes[0,0].set_title('Magnitud de Impedancia')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

axes[0,1].semilogx(freq, np.angle(Z_libre, deg=True), label='Sin caja', linewidth=2)
axes[0,1].semilogx(freq, np.angle(Z_sealed, deg=True), label='Sellada 20L', linewidth=2)
axes[0,1].semilogx(freq, np.angle(Z_br, deg=True), label='Bass-reflex 30L', linewidth=2)
axes[0,1].set_xlabel('Frecuencia [Hz]')
axes[0,1].set_ylabel('Fase [°]')
axes[0,1].set_title('Fase de Impedancia')
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)

# SPL
axes[0,2].semilogx(freq, SPL_libre, label='Sin caja', linewidth=2)
axes[0,2].semilogx(freq, SPL_sealed, label='Sellada 20L', linewidth=2)
axes[0,2].semilogx(freq, SPL_br, label='Bass-reflex 30L', linewidth=2)
axes[0,2].set_xlabel('Frecuencia [Hz]')
axes[0,2].set_ylabel('SPL [dB]')
axes[0,2].set_title('SPL @ 1m (2.83V)')
axes[0,2].legend()
axes[0,2].grid(True, alpha=0.3)

# Fila 2: Desplazamiento
axes[1,0].loglog(freq, np.abs(disp_libre)*1000, label='Sin caja', linewidth=2)
axes[1,0].loglog(freq, np.abs(disp_sealed)*1000, label='Sellada 20L', linewidth=2)
axes[1,0].loglog(freq, np.abs(disp_br)*1000, label='Bass-reflex 30L', linewidth=2)
axes[1,0].set_xlabel('Frecuencia [Hz]')
axes[1,0].set_ylabel('Desplazamiento [mm]')
axes[1,0].set_title('Desplazamiento del Cono')
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)

# Análisis de resonancias
axes[1,1].semilogx(freq, np.abs(Z_libre), label='Sin caja', linewidth=2)
axes[1,1].semilogx(freq, np.abs(Z_sealed), label='Sellada 20L', linewidth=2)
axes[1,1].semilogx(freq, np.abs(Z_br), label='Bass-reflex 30L', linewidth=2)
axes[1,1].set_xlabel('Frecuencia [Hz]')
axes[1,1].set_ylabel('Impedancia [Ω]')
axes[1,1].set_title('Zoom: Resonancias')
axes[1,1].set_xlim([20, 200])
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

# Información de resonancias
axes[1,2].text(0.1, 0.9, 'RESONANCIAS DETECTADAS:', transform=axes[1,2].transAxes, fontweight='bold')
axes[1,2].text(0.1, 0.8, f'Driver libre @ Fs: {52} Hz', transform=axes[1,2].transAxes)

# Buscar picos en impedancia
from scipy.signal import find_peaks

peaks_sealed, _ = find_peaks(np.abs(Z_sealed), height=np.max(np.abs(Z_sealed))*0.8)
peaks_br, _ = find_peaks(np.abs(Z_br), height=np.max(np.abs(Z_br))*0.8)

if len(peaks_sealed) > 0:
    axes[1,2].text(0.1, 0.7, f'Sellada: {freq[peaks_sealed[0]]:.1f} Hz', transform=axes[1,2].transAxes)
else:
    axes[1,2].text(0.1, 0.7, 'Sellada: Sin picos claros', transform=axes[1,2].transAxes)

if len(peaks_br) > 0:
    axes[1,2].text(0.1, 0.6, f'Bass-reflex: {freq[peaks_br[0]]:.1f} Hz', transform=axes[1,2].transAxes)
    if len(peaks_br) > 1:
        axes[1,2].text(0.1, 0.5, f'            + {freq[peaks_br[1]]:.1f} Hz', transform=axes[1,2].transAxes)
else:
    axes[1,2].text(0.1, 0.6, 'Bass-reflex: Sin picos claros', transform=axes[1,2].transAxes)

# Información de rangos
axes[1,2].text(0.1, 0.4, 'VALORES TÍPICOS:', transform=axes[1,2].transAxes, fontweight='bold')
axes[1,2].text(0.1, 0.3, f'Z @ 1kHz: {np.abs(Z_libre[-20]):.1f} Ω (libre)', transform=axes[1,2].transAxes)
axes[1,2].text(0.1, 0.2, f'SPL @ 1kHz: {SPL_libre[-20]:.1f} dB (libre)', transform=axes[1,2].transAxes)
axes[1,2].text(0.1, 0.1, f'Despl @ 50Hz: {np.abs(disp_libre[np.argmin(np.abs(freq-50))])*1000:.2f} mm', transform=axes[1,2].transAxes)

axes[1,2].set_xlim([0, 1])
axes[1,2].set_ylim([0, 1])
axes[1,2].axis('off')

plt.tight_layout()
plt.savefig('outputs/test_completo_metricas.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n✅ Test completo finalizado.")
print(f"📊 Gráfica guardada en 'outputs/test_completo_metricas.png'")
print(f"🔍 Picos en sellada: {len(peaks_sealed)}")
print(f"🔍 Picos en bass-reflex: {len(peaks_br)}")

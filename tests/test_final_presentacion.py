# Test final para presentación - Verificar bass-reflex correcto
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
    "Fs": 50, 
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

# Frecuencias con alta resolución para presentación
freq = np.logspace(1, 3, 500)  # 10 Hz a 1 kHz

print("=== TEST FINAL PARA PRESENTACIÓN ===")

# Configuraciones para presentar
driver_libre = Driver(params, enclosure=None)
sealed = SealedBox(25)  # 25 litros
bassreflex = BassReflexBox(25, 0.008, 0.12)  # 25L, puerto 0.008m², 0.12m

# Información del puerto
print(f"Frecuencia del puerto: {bassreflex.fp:.1f} Hz")

driver_sealed = Driver(params, enclosure=sealed)
driver_br = Driver(params, enclosure=bassreflex)

# Calcular todas las métricas
print("Calculando métricas...")
Z_libre = driver_libre.impedance(freq)
Z_sealed = driver_sealed.impedance(freq)
Z_br = driver_br.impedance(freq)

SPL_libre = driver_libre.spl_total(freq)
SPL_sealed = driver_sealed.spl_total(freq)
SPL_br = driver_br.spl_total(freq)

disp_libre = driver_libre.displacement(freq)
disp_sealed = driver_sealed.displacement(freq)
disp_br = driver_br.displacement(freq)

# Crear gráfica profesional para presentación
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Simulación de Sistema de Altavoces - Comparación de Recintos', fontsize=16, fontweight='bold')

# Impedancia
axes[0,0].semilogx(freq, np.abs(Z_libre), 'k-', linewidth=2.5, label='Infinite Baffle')
axes[0,0].semilogx(freq, np.abs(Z_sealed), 'b-', linewidth=2.5, label='Caja Sellada 25L')
axes[0,0].semilogx(freq, np.abs(Z_br), 'r-', linewidth=2.5, label=f'Bass-Reflex 25L (fp={bassreflex.fp:.1f}Hz)')
axes[0,0].axvline(x=bassreflex.fp, color='gray', linestyle='--', alpha=0.7, label='Frecuencia del puerto')
axes[0,0].set_xlabel('Frecuencia [Hz]', fontsize=12)
axes[0,0].set_ylabel('Impedancia [Ω]', fontsize=12)
axes[0,0].set_title('Impedancia Eléctrica', fontsize=14, fontweight='bold')
axes[0,0].legend(fontsize=10)
axes[0,0].grid(True, alpha=0.3)
axes[0,0].set_xlim([20, 1000])

# SPL
axes[0,1].semilogx(freq, SPL_libre, 'k-', linewidth=2.5, label='Infinite Baffle')
axes[0,1].semilogx(freq, SPL_sealed, 'b-', linewidth=2.5, label='Caja Sellada 25L')
axes[0,1].semilogx(freq, SPL_br, 'r-', linewidth=2.5, label=f'Bass-Reflex 25L')
axes[0,1].axvline(x=bassreflex.fp, color='gray', linestyle='--', alpha=0.7, label='Frecuencia del puerto')
axes[0,1].set_xlabel('Frecuencia [Hz]', fontsize=12)
axes[0,1].set_ylabel('SPL [dB @ 1m, 2.83V]', fontsize=12)
axes[0,1].set_title('Respuesta en Frecuencia (SPL)', fontsize=14, fontweight='bold')
axes[0,1].legend(fontsize=10)
axes[0,1].grid(True, alpha=0.3)
axes[0,1].set_xlim([20, 1000])

# Desplazamiento
axes[1,0].loglog(freq, np.abs(disp_libre)*1000, 'k-', linewidth=2.5, label='Infinite Baffle')
axes[1,0].loglog(freq, np.abs(disp_sealed)*1000, 'b-', linewidth=2.5, label='Caja Sellada 25L')
axes[1,0].loglog(freq, np.abs(disp_br)*1000, 'r-', linewidth=2.5, label='Bass-Reflex 25L')
axes[1,0].axvline(x=bassreflex.fp, color='gray', linestyle='--', alpha=0.7)
axes[1,0].set_xlabel('Frecuencia [Hz]', fontsize=12)
axes[1,0].set_ylabel('Desplazamiento [mm]', fontsize=12)
axes[1,0].set_title('Desplazamiento del Cono', fontsize=14, fontweight='bold')
axes[1,0].legend(fontsize=10)
axes[1,0].grid(True, alpha=0.3)
axes[1,0].set_xlim([20, 1000])

# Fase de impedancia
axes[1,1].semilogx(freq, np.angle(Z_libre, deg=True), 'k-', linewidth=2.5, label='Infinite Baffle')
axes[1,1].semilogx(freq, np.angle(Z_sealed, deg=True), 'b-', linewidth=2.5, label='Caja Sellada 25L')
axes[1,1].semilogx(freq, np.angle(Z_br, deg=True), 'r-', linewidth=2.5, label='Bass-Reflex 25L')
axes[1,1].axvline(x=bassreflex.fp, color='gray', linestyle='--', alpha=0.7)
axes[1,1].set_xlabel('Frecuencia [Hz]', fontsize=12)
axes[1,1].set_ylabel('Fase [°]', fontsize=12)
axes[1,1].set_title('Fase de Impedancia', fontsize=14, fontweight='bold')
axes[1,1].legend(fontsize=10)
axes[1,1].grid(True, alpha=0.3)
axes[1,1].set_xlim([20, 1000])

plt.tight_layout()
plt.subplots_adjust(top=0.93)
plt.savefig('outputs/presentacion_final.png', dpi=300, bbox_inches='tight')
plt.show()

# Análisis cuantitativo
print("\n=== ANÁLISIS CUANTITATIVO ===")
print(f"Frecuencia del puerto: {bassreflex.fp:.1f} Hz")

# Encontrar valores en frecuencias clave
idx_50 = np.argmin(np.abs(freq - 50))
idx_100 = np.argmin(np.abs(freq - 100))
idx_port = np.argmin(np.abs(freq - bassreflex.fp))

print(f"\nA 50 Hz:")
print(f"  Z libre: {np.abs(Z_libre[idx_50]):.1f} Ω")
print(f"  Z sellada: {np.abs(Z_sealed[idx_50]):.1f} Ω")
print(f"  Z bass-reflex: {np.abs(Z_br[idx_50]):.1f} Ω")

print(f"\nA {bassreflex.fp:.1f} Hz (puerto):")
print(f"  Z libre: {np.abs(Z_libre[idx_port]):.1f} Ω")
print(f"  Z sellada: {np.abs(Z_sealed[idx_port]):.1f} Ω")
print(f"  Z bass-reflex: {np.abs(Z_br[idx_port]):.1f} Ω")

print(f"\nSPL a 100 Hz:")
print(f"  SPL libre: {SPL_libre[idx_100]:.1f} dB")
print(f"  SPL sellada: {SPL_sealed[idx_100]:.1f} dB")
print(f"  SPL bass-reflex: {SPL_br[idx_100]:.1f} dB")

# Verificar diferencias
diff_Z = np.abs(Z_br[idx_port] - Z_sealed[idx_port])
diff_SPL = SPL_br[idx_100] - SPL_sealed[idx_100]

print(f"\nDiferencias significativas:")
print(f"  Δ Impedancia @ fp: {diff_Z:.2f} Ω")
print(f"  Δ SPL @ 100Hz: {diff_SPL:.1f} dB")

if diff_Z > 1.0:
    print("✅ Bass-reflex muestra comportamiento diferenciado en impedancia")
else:
    print("⚠️ Bass-reflex no muestra suficiente diferencia en impedancia")

if abs(diff_SPL) > 3.0:
    print("✅ Bass-reflex muestra diferencia significativa en SPL")
else:
    print("⚠️ Bass-reflex no muestra suficiente diferencia en SPL")

print(f"\n📊 Gráfica final guardada en 'outputs/presentacion_final.png'")
print("🎯 Listo para presentación")

#!/usr/bin/env python3
"""
TEST FINAL PARA PRESENTACIÓN - VERSIÓN CORREGIDA
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from core.driver import Driver
from core.sealed import SealedBox
from core.bassreflex import BassReflexBox

# Parámetros del driver para presentación
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

freq = np.logspace(1, 3, 500)  # Alta resolución para presentación

print("=== TEST FINAL PARA PRESENTACIÓN - VERSIÓN CORREGIDA ===")

# Configuraciones
driver_libre = Driver(params, enclosure=None)
sealed = SealedBox(25)  # 25 litros
driver_sealed = Driver(params, enclosure=sealed)
bassreflex = BassReflexBox(25, 0.01, 0.10)  # 25L, puerto óptimo
driver_br = Driver(params, enclosure=bassreflex)

print(f"Frecuencia del puerto: {bassreflex.fp:.1f} Hz")

# Calcular todas las métricas
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

# Crear gráfica profesional para presentación
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Sistema de Simulación de Altavoces (SSS) - Análisis Completo', fontsize=16, fontweight='bold')

# Impedancia Eléctrica
axes[0,0].semilogx(freq, np.abs(Z_libre), 'k-', linewidth=2.5, label='Infinite Baffle')
axes[0,0].semilogx(freq, np.abs(Z_sealed), 'b-', linewidth=2.5, label=f'Caja Sellada 25L')
axes[0,0].semilogx(freq, np.abs(Z_br), 'r-', linewidth=2.5, label=f'Bass-Reflex 25L (fp={bassreflex.fp:.0f}Hz)')
axes[0,0].axvline(x=bassreflex.fp, color='gray', linestyle='--', alpha=0.7, label='Frecuencia del puerto')
axes[0,0].set_xlabel('Frecuencia [Hz]', fontsize=12)
axes[0,0].set_ylabel('Impedancia [Ω]', fontsize=12)
axes[0,0].set_title('Impedancia Eléctrica', fontsize=14, fontweight='bold')
axes[0,0].legend(fontsize=10)
axes[0,0].grid(True, alpha=0.3)
axes[0,0].set_xlim([20, 1000])
axes[0,0].set_ylim([5, 100])

# SPL
axes[0,1].semilogx(freq, SPL_libre, 'k-', linewidth=2.5, label='Infinite Baffle')
axes[0,1].semilogx(freq, SPL_sealed, 'b-', linewidth=2.5, label='Caja Sellada 25L')
axes[0,1].semilogx(freq, SPL_br, 'r-', linewidth=2.5, label='Bass-Reflex 25L')
axes[0,1].axvline(x=bassreflex.fp, color='gray', linestyle='--', alpha=0.7, label='Frecuencia del puerto')
axes[0,1].set_xlabel('Frecuencia [Hz]', fontsize=12)
axes[0,1].set_ylabel('SPL [dB @ 1m, 2.83V]', fontsize=12)
axes[0,1].set_title('Respuesta en Frecuencia (SPL)', fontsize=14, fontweight='bold')
axes[0,1].legend(fontsize=10)
axes[0,1].grid(True, alpha=0.3)
axes[0,1].set_xlim([20, 1000])

# Desplazamiento del cono
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
plt.savefig('outputs/presentacion_final_corregida.png', dpi=300, bbox_inches='tight')
print("📊 Gráfica guardada en 'outputs/presentacion_final_corregida.png'")

# Análisis cuantitativo para presentación
print("\n=== ANÁLISIS CUANTITATIVO PARA PRESENTACIÓN ===")
idx_50 = np.argmin(np.abs(freq - 50))
idx_fp = np.argmin(np.abs(freq - bassreflex.fp))
idx_100 = np.argmin(np.abs(freq - 100))

print(f"Frecuencia del puerto bass-reflex: {bassreflex.fp:.1f} Hz")
print(f"\n📊 IMPEDANCIA @ 50 Hz:")
print(f"   Infinite Baffle: {np.abs(Z_libre[idx_50]):.1f} Ω")
print(f"   Caja Sellada:    {np.abs(Z_sealed[idx_50]):.1f} Ω")
print(f"   Bass-Reflex:     {np.abs(Z_br[idx_50]):.1f} Ω")

print(f"\n📊 IMPEDANCIA @ {bassreflex.fp:.0f} Hz (puerto):")
print(f"   Infinite Baffle: {np.abs(Z_libre[idx_fp]):.1f} Ω")
print(f"   Caja Sellada:    {np.abs(Z_sealed[idx_fp]):.1f} Ω")
print(f"   Bass-Reflex:     {np.abs(Z_br[idx_fp]):.1f} Ω")

print(f"\n📊 SPL @ 100 Hz:")
print(f"   Infinite Baffle: {SPL_libre[idx_100]:.1f} dB")
print(f"   Caja Sellada:    {SPL_sealed[idx_100]:.1f} dB")
print(f"   Bass-Reflex:     {SPL_br[idx_100]:.1f} dB")

print(f"\n📊 RANGOS COMPLETOS:")
print(f"   Z Infinite Baffle: {np.min(np.abs(Z_libre)):.1f} - {np.max(np.abs(Z_libre)):.1f} Ω")
print(f"   Z Caja Sellada:    {np.min(np.abs(Z_sealed)):.1f} - {np.max(np.abs(Z_sealed)):.1f} Ω")
print(f"   Z Bass-Reflex:     {np.min(np.abs(Z_br)):.1f} - {np.max(np.abs(Z_br)):.1f} Ω")

# Verificación final
diferencia_Z = np.abs(Z_br[idx_fp] - Z_sealed[idx_fp])
diferencia_SPL = SPL_br[idx_100] - SPL_sealed[idx_100]

print(f"\n✅ VERIFICACIÓN FINAL:")
print(f"   Diferencia impedancia @ puerto: {diferencia_Z:.1f} Ω")
print(f"   Diferencia SPL @ 100Hz: {diferencia_SPL:.1f} dB")

if diferencia_Z > 2.0:
    print("✅ Bass-reflex muestra comportamiento distintivo en impedancia")
else:
    print("⚠️ Diferencia en impedancia podría ser mayor")

if abs(diferencia_SPL) > 1.0:
    print("✅ Bass-reflex muestra comportamiento distintivo en SPL")
else:
    print("⚠️ Diferencia en SPL podría ser mayor")

print("\n🎯 ¡SISTEMA LISTO PARA PRESENTACIÓN!")
print("📁 Archivo: outputs/presentacion_final_corregida.png")
print("=== FIN TEST PRESENTACIÓN ===")

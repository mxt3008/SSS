# Debug del modelo bass-reflex paso a paso
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from core.driver import Driver
from core.sealed import SealedBox
from core.bassreflex import BassReflexBox

# Parámetros simplificados
params = {
    "Fs": 50, 
    "Mms": 0.065, 
    "Vas": 62, 
    "Qts": 0.35, 
    "Qes": 0.4, 
    "Qms": 4.0,
    "Re": 6.0, 
    "Bl": 15.0, 
    "Sd": 0.055, 
    "Le": 1.0e-3, 
    "Xmax": 7.5
}

freq = np.logspace(1, 2.5, 200)

print("=== DEBUG BASS-REFLEX PASO A PASO ===")

# Test 1: Driver libre (sin caja)
print("\n1. Driver libre:")
driver_libre = Driver(params, enclosure=None)
Z_libre = driver_libre.impedance(freq)
print(f"   Z @ Fs (50Hz): {np.abs(Z_libre[np.argmin(np.abs(freq - 50))]):.2f} Ω")
print(f"   Z @ 100Hz: {np.abs(Z_libre[np.argmin(np.abs(freq - 100))]):.2f} Ω")

# Test 2: Solo verificar impedancia acústica
print("\n2. Verificando impedancia acústica bass-reflex:")
br = BassReflexBox(30, 0.01, 0.10)  # 30L, puerto 0.01m², 0.1m largo

# Calcular impedancia acústica directamente
f_test = 50
Za_br = br.acoustic_load(f_test, params["Sd"])
print(f"   Za_bass_reflex @ 50Hz: {Za_br:.3e}")

# Comparar con sellada
sealed = SealedBox(30)
Za_sealed = sealed.acoustic_load(f_test, params["Sd"])
print(f"   Za_sellada @ 50Hz: {Za_sealed:.3e}")

# Test 3: Comparar todo el sistema
print("\n3. Sistema completo:")
driver_br = Driver(params, enclosure=br)
driver_sealed = Driver(params, enclosure=sealed)

Z_br = driver_br.impedance(freq)
Z_sealed = driver_sealed.impedance(freq)

print(f"   Z_total BR @ 50Hz: {np.abs(Z_br[np.argmin(np.abs(freq - 50))]):.2f} Ω")
print(f"   Z_total Sealed @ 50Hz: {np.abs(Z_sealed[np.argmin(np.abs(freq - 50))]):.2f} Ω")

# Test 4: Verificar frecuencia de puerto
Vb = 30e-3  # m³
Sp = 0.01   # m²
Lp = 0.10   # m
a_port = np.sqrt(Sp / np.pi)
delta = 0.85 * a_port
Leff = Lp + 2 * delta
rho0 = 1.225
c = 343

# Frecuencia Helmholtz
Map = rho0 * Leff / Sp
Cab = Vb / (rho0 * c**2)
fp = (1 / (2 * np.pi)) * np.sqrt(1 / (Map * Cab))

print(f"\n4. Parámetros del puerto:")
print(f"   Área puerto: {Sp*1e4:.1f} cm²")
print(f"   Largo efectivo: {Leff*1000:.1f} mm")
print(f"   Masa acústica: {Map:.3e} kg/m⁴")
print(f"   Compliance caja: {Cab:.3e} m⁵/N")
print(f"   Frecuencia Helmholtz: {fp:.1f} Hz")

# Plot
plt.figure(figsize=(12, 8))

plt.subplot(2, 2, 1)
plt.semilogx(freq, np.abs(Z_libre), 'k-', linewidth=2, label='Libre')
plt.semilogx(freq, np.abs(Z_sealed), 'b-', linewidth=2, label='Sellada')
plt.semilogx(freq, np.abs(Z_br), 'r-', linewidth=2, label='Bass-reflex')
plt.axvline(x=fp, color='gray', linestyle='--', alpha=0.7, label=f'fp={fp:.1f}Hz')
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('|Z| [Ω]')
plt.title('Magnitud de Impedancia')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xlim([20, 200])

plt.subplot(2, 2, 2)
plt.semilogx(freq, np.angle(Z_libre, deg=True), 'k-', linewidth=2, label='Libre')
plt.semilogx(freq, np.angle(Z_sealed, deg=True), 'b-', linewidth=2, label='Sellada')
plt.semilogx(freq, np.angle(Z_br, deg=True), 'r-', linewidth=2, label='Bass-reflex')
plt.axvline(x=fp, color='gray', linestyle='--', alpha=0.7)
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Fase [°]')
plt.title('Fase de Impedancia')
plt.legend()
plt.grid(True, alpha=0.3)
plt.xlim([20, 200])

# Impedancias acústicas
plt.subplot(2, 2, 3)
Za_br_array = []
Za_sealed_array = []

for f in freq:
    Za_br_array.append(br.acoustic_load(f, params["Sd"]))
    Za_sealed_array.append(sealed.acoustic_load(f, params["Sd"]))

Za_br_array = np.array(Za_br_array)
Za_sealed_array = np.array(Za_sealed_array)

plt.loglog(freq, np.abs(Za_br_array), 'r-', linewidth=2, label='BR acoustic load')
plt.loglog(freq, np.abs(Za_sealed_array), 'b-', linewidth=2, label='Sealed acoustic load')
plt.axvline(x=fp, color='gray', linestyle='--', alpha=0.7)
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('|Za| [N·s/m]')
plt.title('Impedancia Acústica')
plt.legend()
plt.grid(True, alpha=0.3)

# Diferencia relativa
plt.subplot(2, 2, 4)
diff_rel = np.abs((np.abs(Z_br) - np.abs(Z_sealed)) / np.abs(Z_sealed)) * 100
plt.semilogx(freq, diff_rel, 'g-', linewidth=2)
plt.axvline(x=fp, color='gray', linestyle='--', alpha=0.7)
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Diferencia relativa [%]')
plt.title('Diferencia BR vs Sellada')
plt.grid(True, alpha=0.3)
plt.xlim([20, 200])

plt.tight_layout()
plt.savefig('outputs/debug_bassreflex.png', dpi=150, bbox_inches='tight')
plt.show()

print(f"\n✅ Debug completado. Gráfica guardada en 'outputs/debug_bassreflex.png'")

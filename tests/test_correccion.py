# Test rápido para verificar las correcciones
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
freq = np.logspace(1, 3, 100)  # 10 Hz a 1 kHz

print("=== TEST DE CORRECCIONES ===")

# Test 1: Driver sin caja (infinite baffle)
print("\n1. Driver sin caja:")
driver_libre = Driver(params, enclosure=None)
Z_libre = driver_libre.impedance(freq)
print(f"   Impedancia @ Fs: {np.abs(Z_libre[np.argmin(np.abs(freq - 52))]):.2f} Ω")
print(f"   Impedancia @ 1kHz: {np.abs(Z_libre[-10]):.2f} Ω")

# Test 2: Caja sellada
print("\n2. Caja sellada (20L):")
sealed = SealedBox(20)  # 20 litros
driver_sealed = Driver(params, enclosure=sealed)
Z_sealed = driver_sealed.impedance(freq)
print(f"   Impedancia @ Fs: {np.abs(Z_sealed[np.argmin(np.abs(freq - 52))]):.2f} Ω")
print(f"   Impedancia @ 1kHz: {np.abs(Z_sealed[-10]):.2f} Ω")

# Test 3: Bass-reflex
print("\n3. Bass-reflex (30L, puerto 0.01m², 0.1m):")
bassreflex = BassReflexBox(30, 0.01, 0.1)  # 30L, 0.01m², 0.1m
driver_br = Driver(params, enclosure=bassreflex)
Z_br = driver_br.impedance(freq)
print(f"   Impedancia @ Fs: {np.abs(Z_br[np.argmin(np.abs(freq - 52))]):.2f} Ω")
print(f"   Impedancia @ 1kHz: {np.abs(Z_br[-10]):.2f} Ω")

# Verificar si hay valores extremos
print("\n=== VERIFICACIÓN DE VALORES ===")
print(f"Driver libre - min/max Z: {np.min(np.abs(Z_libre)):.2f} / {np.max(np.abs(Z_libre)):.2f} Ω")
print(f"Caja sellada - min/max Z: {np.min(np.abs(Z_sealed)):.2f} / {np.max(np.abs(Z_sealed)):.2f} Ω")
print(f"Bass-reflex - min/max Z: {np.min(np.abs(Z_br)):.2f} / {np.max(np.abs(Z_br)):.2f} Ω")

# Plot rápido
plt.figure(figsize=(10, 6))
plt.subplot(121)
plt.semilogx(freq, np.abs(Z_libre), label='Sin caja')
plt.semilogx(freq, np.abs(Z_sealed), label='Sellada 20L')
plt.semilogx(freq, np.abs(Z_br), label='Bass-reflex 30L')
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Impedancia [Ω]')
plt.title('Impedancia corregida')
plt.legend()
plt.grid(True)

plt.subplot(122)
plt.semilogx(freq, np.angle(Z_libre, deg=True), label='Sin caja')
plt.semilogx(freq, np.angle(Z_sealed, deg=True), label='Sellada 20L')
plt.semilogx(freq, np.angle(Z_br, deg=True), label='Bass-reflex 30L')
plt.xlabel('Frecuencia [Hz]')
plt.ylabel('Fase [°]')
plt.title('Fase de impedancia')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig('test_correccion_impedancia.png', dpi=150)
plt.show()

print("\n✅ Test completado. Gráfica guardada como 'test_correccion_impedancia.png'")

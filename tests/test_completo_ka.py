#!/usr/bin/env python3
# Test completo para verificar todas las rutas de simulación

from core.driver import Driver
import numpy as np

print("=== TEST COMPLETO DE LÍMITES DE KA ===")
print()

# Usar los parámetros del main.py
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

# Calcular Cms desde Vas (necesario para Driver)
rho0 = 1.2  # densidad aire
c = 344     # velocidad sonido
Vas_m3 = params["Vas"] / 1000  # convertir litros a m³
params["Cms"] = Vas_m3 / (rho0 * c**2 * params["Sd"]**2)

driver = Driver(params)

print("1. TEST DE SIMULACIÓN NORMAL (como app.py y driver normal en app_qt5.py):")
f_max_normal = driver.f_max_ka(ka_max=1.0)
print(f"   f_max calculado: {f_max_normal:.2f} Hz")
frequencies_normal = np.logspace(np.log10(5), np.log10(f_max_normal), 1000)
print(f"   Rango de simulación: {frequencies_normal[0]:.1f} Hz a {frequencies_normal[-1]:.1f} Hz")
print()

print("2. TEST DE SIMULACIÓN BANDPASS (como en app_qt5.py después de corrección):")
# Simular exactamente lo que hace el código corregido
temp_params = {
    'Re': params['Re'],
    'Qes': params['Qes'], 
    'Qms': params['Qms'],
    'Fs': params['Fs'],
    'Bl': params['Bl'],
    'Sd': params['Sd'],
    'Vas': 0.05,  # valor temporal
    'Xmax': 7.5   # valor temporal
}
# Calcular Cms desde Vas temporal
Vas_m3_temp = temp_params["Vas"] / 1000
temp_params["Cms"] = Vas_m3_temp / (rho0 * c**2 * temp_params["Sd"]**2)
temp_driver = Driver(temp_params)
f_max_bandpass = temp_driver.f_max_ka(ka_max=1.0)
print(f"   f_max calculado: {f_max_bandpass:.2f} Hz")
frequencies_bandpass = np.logspace(np.log10(5), np.log10(f_max_bandpass), 1000)
print(f"   Rango de simulación: {frequencies_bandpass[0]:.1f} Hz a {frequencies_bandpass[-1]:.1f} Hz")
print()

print("3. VERIFICACIÓN DE ka EN FRECUENCIAS TÍPICAS:")
a = np.sqrt(params["Sd"] / np.pi)
print(f"   Radio equivalente a = {a:.4f} m")
frecuencias_test = [100, 200, 400, 500, 1000, 2000, 5000]
for f in frecuencias_test:
    ka = 2 * np.pi * f * a / c
    status = "✓ VÁLIDO" if ka <= 1.0 else "✗ INVÁLIDO"
    print(f"   f = {f:4d} Hz  ->  ka = {ka:.3f}  {status}")

print()
print("=== CONCLUSIÓN ===")
print(f"La aplicación DEBE simular MÁXIMO hasta ~{f_max_normal:.0f} Hz")
print("Si ves simulaciones hasta 10kHz o 20kHz, hay un ERROR.")

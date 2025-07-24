#!/usr/bin/env python3
# Test para verificar el límite de frecuencia ka después de las correcciones

from core.driver import Driver
import numpy as np

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

# Calcular frecuencias máximas para diferentes valores de ka
f_max_ka1 = driver.f_max_ka(ka_max=1.0)
f_max_ka05 = driver.f_max_ka(ka_max=0.5)

print(f'=== VERIFICACIÓN DE LÍMITES DE KA ===')
print(f'')
print(f'Parámetros del driver:')
print(f'Sd = {driver.Sd} m²')
print(f'Radio equivalente a = {np.sqrt(driver.Sd / np.pi):.4f} m')
print(f'Velocidad del sonido c = {driver.c} m/s')
print(f'')
print(f'Frecuencia máxima con ka=1.0: {f_max_ka1:.2f} Hz')
print(f'Frecuencia máxima con ka=0.5: {f_max_ka05:.2f} Hz')
print(f'')
print(f'=== ESTADO ACTUAL DE LA APLICACIÓN ===')
print(f'Con los parámetros actuales, la aplicación debería simular')
print(f'MÁXIMO hasta {f_max_ka1:.0f} Hz para respetar ka ≤ 1')
print(f'')
print(f'Si ves simulaciones hasta 10kHz o 20kHz, entonces')
print(f'hay un problema que necesita ser corregido.')

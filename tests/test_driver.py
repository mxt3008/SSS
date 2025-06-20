# tests/test_driver.py

from core.driver import Driver
import numpy as np
import pytest

# ------------------------
# Parámetros base comunes para todos los tests
# Incluye al menos dos de {Fs, Mms, Cms}
# ------------------------
params = {
    "Fs": 40,
    "Mms": 0.02,  # Opcional - para evitar ValueError (20 gramos)
    "Vas": 50,
    "Qts": 0.35,
    "Qes": 0.4,
    "Re": 6.0,
    "Bl": 7.5,
    "Sd": 0.02,
    "Le": 0.0005,
    "Xmax": 0.005
}

# ------------------------
# Test: La impedancia debe ser un número complejo y su parte real positiva
# ------------------------
def test_impedance_is_complex():
    driver = Driver(params)
    Z = driver.impedance(40)
    assert isinstance(Z, complex), "Impedancia debe ser compleja"
    assert Z.real > 0, "Parte real de la impedancia debe ser positiva"

# ------------------------
# Test: El SPL debe ser un número realista y dentro de un rango físico razonable
# ------------------------
def test_spl_response_valid():
    driver = Driver(params)
    spl = driver.spl_response(100)
    assert isinstance(spl, (float, int)), "SPL debe ser un número"
    assert 70 < spl < 120, f"SPL parece irreal: {spl} dB"

# ------------------------
# Test: Los parámetros derivados deben ser positivos
# ------------------------
def test_derived_parameters_positive():
    driver = Driver(params)
    assert driver.Mms > 0, f"Mms debe ser positivo: {driver.Mms}"
    assert driver.Cms > 0, f"Cms debe ser positivo: {driver.Cms}"
    assert driver.Rms > 0, f"Rms debe ser positivo: {driver.Rms}"
    assert driver.Kms > 0, f"Kms debe ser positivo: {driver.Kms}"
    assert driver.rho0 > 0, f"rho0 debe ser positivo: {driver.rho0}"
    assert driver.c > 0, f"c debe ser positivo: {driver.c}"

# ------------------------
# Test: Consistencia física entre Kms, Mms y Cms
#  - Kms ≈ Mms * w0²
#  - Cms ≈ 1/Kms
# ------------------------
def test_physical_consistency():
    driver = Driver(params)
    w0 = 2 * np.pi * driver.Fs
    kms = driver.Kms  # Usar el Kms derivado en __init__, no recalcular
    assert kms == pytest.approx(driver.Mms * w0**2, rel=1e-3), "Kms inconsistente con Mms y Fs"
    assert driver.Cms == pytest.approx(1 / kms, rel=1e-3), "Cms inconsistente con Kms"

# ------------------------
# Test: La excursión pico debe ser mayor en baja frecuencia que en alta frecuencia
# Además, la excursión en bajas frecuencias debe ser significativa respecto a Xmax
# ------------------------
def test_excursion_behavior():
    driver = Driver(params)
    v_low = abs(driver.velocity(10))
    v_high = abs(driver.velocity(1000))
    excursion_low = v_low / (2 * np.pi * 10)
    excursion_high = v_high / (2 * np.pi * 1000)
    assert excursion_low > excursion_high, (
        f"Excursión inesperada: baja={excursion_low:.4e} m, alta={excursion_high:.4e} m"
    )
    assert excursion_low > driver.Xmax * 0.5, (
        "Excursión en baja frecuencia debería ser significativa respecto a Xmax"
    )

# ------------------------
# Test: La densidad del aire y la velocidad del sonido deben ser consistentes con la temperatura y presión
# ------------------------
def test_air_properties():
    driver = Driver(params)
    # Valores típicos a 20°C y 101325 Pa: rho0 ≈ 1.204 kg/m³, c ≈ 343 m/s
    assert 1.1 < driver.rho0 < 1.3, f"rho0 fuera de rango típico: {driver.rho0}"
    assert 340 < driver.c < 350, f"c fuera de rango típico: {driver.c}"

# ------------------------
# Test: La eficiencia debe ser un valor pequeño y positivo
# ------------------------
def test_efficiency():
    driver = Driver(params)
    eta = driver.efficiency()
    assert eta > 0, f"Eficiencia debe ser positiva: {eta}"
    assert eta < 0.1, f"Eficiencia irrealmente alta: {eta}"

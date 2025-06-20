# tests/test_driver.py

from core.driver import Driver
import numpy as np
import pytest

# ------------------------
# Parámetros base comunes
# ------------------------
params = {
    "Fs": 40,
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
# 1) Impedancia
# ------------------------
def test_impedance_is_complex():
    driver = Driver(params)
    Z = driver.impedance(40)
    assert isinstance(Z, complex), "Impedancia debe ser un número complejo"
    assert Z.real > 0, "Parte real de la impedancia debe ser positiva"

def test_impedance_return_type():
    driver = Driver(params)
    Z = driver.impedance(100)
    assert isinstance(Z, complex), "Impedancia debe ser compleja"

# ------------------------
# 2) SPL
# ------------------------
def test_spl_response_valid():
    driver = Driver(params)
    spl = driver.spl_response(100)
    assert isinstance(spl, (float, int)), "SPL debe ser un número"
    assert 70 < spl < 120, f"SPL parece irreal: {spl} dB"

# ------------------------
# 3) Derivados positivos
# ------------------------
def test_derived_parameters_positive():
    driver = Driver(params)
    assert driver.Mms > 0, f"Mms debe ser positivo: {driver.Mms}"
    assert driver.Cms > 0, f"Cms debe ser positivo: {driver.Cms}"
    assert driver.Rms > 0, f"Rms debe ser positivo: {driver.Rms}"

# ------------------------
# 4) Consistencia física: Kms ≈ Mms * w0², Cms ≈ 1/Kms
# ------------------------
def test_physical_consistency():
    driver = Driver(params)
    w0 = 2 * np.pi * driver.Fs
    kms = driver.derive_Kms()
    assert kms == pytest.approx(driver.Mms * w0**2, rel=1e-3), f"Kms inconsistente"
    assert driver.Cms == pytest.approx(1 / kms, rel=1e-3), f"Cms inconsistente con Kms"

# ------------------------
# 5) Excursión pico: baja frecuencia >> alta frecuencia
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
    # Además, prueba que la excursión en bajas frecuencias excede Xmax
    assert excursion_low > driver.Xmax * 0.5, (
        f"Excursión baja frecuencia debería ser significativa respecto a Xmax"
    )

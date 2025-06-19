# tests/test_driver.py

from core.driver import Driver
import numpy as np

def test_impedance_is_complex():
    # Verifica que la impedancia devuelta sea un número complejo, y que su parte real sea mayor que cero."
    params = {
        "Fs": 40,
        "Vas": 50,
        "Qts": 0.35,
        "Qes": 0.4,
        "Re": 6.0,
        "Bl": 7.5,
        "Sd": 0.02,
        "Le": 0.0005
    }
    driver = Driver(params)
    Z = driver.impedance(40)
    assert isinstance(Z, complex), "Impedancia debe ser un número complejo"
    assert Z.real > 0, "Parte real de la impedancia debe ser positiva"

def test_spl_response_valid():
    # Verifica que el SPL devuelto sea un número flotante y dentro de un rango plausible."
    params = {
        "Fs": 40,
        "Vas": 50,
        "Qts": 0.35,
        "Qes": 0.4,
        "Re": 6.0,
        "Bl": 7.5,
        "Sd": 0.02,
        "Le": 0.0005
    }
    driver = Driver(params)
    spl = driver.spl_response(100)
    assert isinstance(spl, (float, int)), "SPL debe ser un número"
    assert 70 < spl < 120, f"SPL parece irreal: {spl} dB"

def test_derived_parameters_positive():
    # Verifica que Mms, Cms y Rms sean positivos y coherentes físicamente."
    params = {
        "Fs": 40,
        "Vas": 50,
        "Qts": 0.35,
        "Qes": 0.4,
        "Re": 6.0,
        "Bl": 7.5,
        "Sd": 0.02,
        "Le": 0.0005
    }
    driver = Driver(params)
    assert driver.Mms > 0, f"Mms debe ser positivo: {driver.Mms}"
    assert driver.Cms > 0, f"Cms debe ser positivo: {driver.Cms}"
    assert driver.Rms > 0, f"Rms debe ser positivo: {driver.Rms}"
 
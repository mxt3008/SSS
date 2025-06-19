# tests/test_driver.py

from core.driver import Driver

def test_impedance_constant():
    "Verifica que la impedancia básica devuelta sea igual a la resistencia Re cuando no hay resonancia modelada aún."
    
    params = {"Fs": 40, "Vas": 50, "Qts": 0.35, "Re": 6.0}
    driver = Driver(params)
    assert driver.impedance(100) == 6.0  # Por ahora, impedancia simple = Re

def test_spl_response_placeholder():
    "Verifica que el método SPL devuelva un valor numérico."

    params = {"Fs": 40, "Vas": 50, "Qts": 0.35, "Re": 6.0}
    driver = Driver(params)
    result = driver.spl_response(100)
    assert isinstance(result, (int, float))

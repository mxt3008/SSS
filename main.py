# main.py

from core.driver import Driver

# Define parámetros de prueba
params = {
    "Fs": 40,
    "Vas": 50,
    "Qts": 0.35,
    "Re": 6.0
}

# Crea una instancia del driver
my_driver = Driver(params)

# Prueba métodos
print("Impedancia a 100 Hz:", my_driver.impedance(100))
print("SPL estimado a 100 Hz:", my_driver.spl_response(100))
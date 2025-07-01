# --------------------------------------------
# main.py
# Script principal para simular y analizar el comportamiento de un parlante en aire libre.
# --------------------------------------------

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

# --------------------------------------------
# Importar librerías necesarias
# --------------------------------------------

import numpy as np                                                          # Para operaciones matemáticas y manejo de arrays
import matplotlib                                                           # Para graficar resultados
matplotlib.use("TkAgg")                                                     # Fuerza el uso del backend TkAgg para mostrar gráficos en ventana
import matplotlib.pyplot as plt                                             # Para crear gráficos y visualizaciones
import matplotlib.ticker as ticker                                          # Para formatear ejes en gráficos
from matplotlib.ticker import LogLocator, FixedLocator, MultipleLocator     # Para formatear ejes logarítmicos y escalares
import mplcursors                                                           # Para agregar cursores interactivos a los gráficos
import tkinter as tk
from tkinter import simpledialog, messagebox

from core.driver import Driver                                              # Importa la clase Driver definida en core/driver.py
from visualization.plots import plot_all

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

# --------------------------------------------
# Definir parámetros del altavoz
# --------------------------------------------

params = {
    "Fs": 52,                                   # Frecuencia de resonancia [Hz]
    "Mms": 0.065,                               # Masa móvil aproximada [kg]
    "Vas": 62,                                  # Volumen de aire equivalente [litros]
    "Qts": 0.32,                                # Factor de calidad total
    "Qes": 0.34,                                # Factor de calidad eléctrico
    "Qms": 4.5,                                 # Factor de calidad mecánico 
    "Re": 5.3,                                  # Resistencia DC de la bobina [Ohm]
    "Bl": 18.1,                                 # Producto flujo-Bobina [N/A]
    "Sd": 0.055,                                # Área efectiva del diafragma [m²]
    "Le": 1.5e-3,                               # Inductancia de la bobina [Henrios]
    "Xmax": 7.5                                 # Excursión máxima lineal del cono [milímetros]
}

units = {
    "Fs": "Hz",                                 # Frecuencia de resonancia
    "Mms": "kg",                                # Masa móvil
    "Vas": "litros",                            # Volumen de aire equivalente
    "Qts": "",                                  # Factor de calidad total 
    "Qes": "",                                  # Factor de calidad eléctrico
    "Qms": "",                                  # Factor de calidad mecánico
    "Re": "Ω",                                  # Resistencia DC de la bobina
    "Bl": "N/A",                                # Producto flujo-Bobina          
    "Sd": "m²",                                 # Área efectiva del diafragma
    "Le": "H",                                  # Inductancia de la bobina
    "Xmax": "mm"                                # Excursión máxima lineal del cono
}

def pedir_parametros(params, units):            # Función para pedir al usuario los parámetros del altavoz
    def on_submit():                            # Función que se ejecuta al hacer clic en el botón "Aceptar"
        for key, entry in entries.items():      # Itera sobre los parámetros introducidos por el usuario
            val = entry.get()                   # Obtiene el valor del campo de entrada
            if val.strip() == "":               # Si el campo está vacío, usa el valor por defecto
                user_params[key] = params[key]  
            else:                               # Si el campo no está vacío, intenta convertirlo a float
                try:    
                    user_params[key] = float(val)
                except ValueError:              # Si no se puede convertir, muestra un mensaje de error
                    user_params[key] = params[key]
        root.destroy()                          # Cierra la ventana de diálogo

    root = tk.Tk()                              # Crea una ventana de diálogo
    root.title("Introduce parámetros TS del altavoz")
    entries = {}                                # Diccionario para almacenar los campos de entrada
    user_params = {}                            # Diccionario para almacenar los parámetros introducidos por el usuario

    row = 0
    for key in params:                          # Itera sobre los parámetros definidos
        unidad = units.get(key, "")             # Obtiene la unidad correspondiente al parámetro
        label_text = f"{key} [{unidad}]"        # Crea el texto de la etiqueta con el nombre del parámetro y su unidad
        tk.Label(root, text=label_text, anchor="w", width=20).grid(row=row, column=0, padx=5, pady=2, sticky="w")
        entry = tk.Entry(root, width=15)    
        entry.insert(0, str(params[key]))   
        entry.grid(row=row, column=1, padx=5, pady=2)
        entries[key] = entry
        row += 1

    submit_btn = tk.Button(root, text="Aceptar", command=on_submit)
    submit_btn.grid(row=row, column=0, columnspan=2, pady=10)

    root.mainloop()
    return user_params                          # Devuelve los parámetros introducidos por el usuario o los valores por defecto

def mostrar_parametros_derivados(driver):       # Función para mostrar los parámetros derivados del altavoz
    resumen = driver.resumen_parametros()
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Parámetros Derivados", resumen)
    root.destroy()

print("\n=====================================================================")
print("=== Simulador de Driver ===")
print("=== Parámetros por defecto utilizados - JBL 2206H ===")
print("\nIntroduce parámetros TS del altavoz (Enter = usa valores por defecto)\n")

params = pedir_parametros(params, units)        # Pide al usuario los parámetros del altavoz, o usa los valores por defecto
my_driver = Driver(params)                      # Crea una instancia de la clase Driver con los parámetros introducidos
mostrar_parametros_derivados(my_driver)         # Muestra los parámetros derivados del altavoz

# --------------------------------------------
# Calcular y mostrar impedancia y SPL para una frecuencia específica
# --------------------------------------------

freq = params["Fs"]                                                         # Usar la frecuencia de resonancia para la prueba puntual
Z = my_driver.impedance(freq)                                               # Calcula la impedancia compleja a esa frecuencia
print("=====================================================================")
print(f"Impedancia (módulo) a {freq} Hz: {abs(Z):.2f}")                     # Imprime el módulo de la impedancia
print(f"Impedancia (fase) a {freq} Hz: {np.angle(Z, deg=True):.2f} °")      # Imprime la fase de la impedancia
print(f"SPL (módulo) a {freq} Hz: {my_driver.spl_total(freq):.2f} dB")      # Imprime el SPL total a esa frecuencia
print(f"SPL (fase) a {freq} Hz: {my_driver.spl_phase(freq):.2f} °")         # Imprime la fase del SPL a esa frecuencia
print("=====================================================================")

# --------------------------------------------
# Barrido de frecuencias para simulación de rango completo
# --------------------------------------------

f_max = my_driver.f_max_ka()                                        # Obtiene la frecuencia máxima del altavoz (frecuencia de corte)
frequencies = np.logspace(np.log10(5), np.log10(f_max), 1000)       # Vector de frecuencias de 5 Hz a 1000 Hz (escala logarítmica)
print(f"Frecuencia máxima para ka ≤ 1: {f_max:.2f} Hz")             # Imprime la frecuencia máxima para ka ≤ 1
print("=====================================================================\n")

# 1. Calcula la impedancia compleja para cada frecuencia
Z_values = np.array([my_driver.impedance(f) for f in frequencies])
Z_magnitude = np.abs(Z_values)                                      # Módulo de la impedancia
Z_phase = np.angle(Z_values, deg=True)                              # Fase de la impedancia en grados

# 2. Calcula la respuesta SPL estimada para cada frecuencia: total + fase acústica
SPL_total = np.array([my_driver.spl_total(f) for f in frequencies]) # SPL total
SPL_phase = np.array([my_driver.spl_phase(f) for f in frequencies]) # Fase del SPL (acústica)

# 3, Calcula el desplazamiento del cono para cada frecuencia
displacements = np.array([my_driver.displacement(f) for f in frequencies])
displacements_mm = displacements * 1000                             # Convertir a milímetros para graficar

# 4. Calcula la velocidad del cono para cada frecuencia (magnitud)
velocities = np.array([abs(my_driver.velocity(f)) for f in frequencies])

# 5. Calcula la potencia acústica para cada frecuencia - Real, aparente y la corriente
# 6. Calcula el retardo de grupo para cada frecuencia
# 7. Calcula la respuesta al escalón para cada frecuencia
# 8. Calcula la eficiencia del altavoz para cada frecuencia

# 9. Calcula la excursión pico del cono para cada frecuencia
excursions = velocities / (2 * np.pi * frequencies)                 # Excursión en metros
excursions_mm = excursions * 1000                                   # Excursión en milímetros
excursion_ratio = excursions / my_driver.Xmax                       # Excursión normalizada respecto a Xmax

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

plot_all(
    my_driver, frequencies, Z_magnitude, Z_phase, SPL_total, SPL_phase,
    displacements_mm, velocities, excursions_mm, excursion_ratio, f_max
)

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

# Fin del script principal

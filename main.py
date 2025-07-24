# --------------------------------------------
# main.py
# Script principal para simular y analizar el comportamiento de un parlante.
# --------------------------------------------

import numpy as np                                                      # Importa numpy para cálculos matemáticos
import matplotlib.pyplot as plt                                         # Importa matplotlib para gráficas
import tkinter as tk                                                    # Importa tkinter para interfaz gráfica alternativa
from tkinter import ttk                                                 # Importa widgets temáticos de tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg         # Backend de matplotlib para tkinter
from core.driver import Driver                                          # Importa la clase Driver del sistema
from visualization.plots import plot_all                                # Importa funciones de visualización
import sys                                                              # Importa sys para manejo del sistema
from visualization.app import App                                       # Importa aplicación tkinter
from visualization.app_qt5 import AppQt                                 # Importa aplicación Qt5
from PyQt5.QtWidgets import QApplication                                # Importa QApplication de PyQt5

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

params = {
    "Fs": 52,                                                           # Frecuencia de resonancia en Hz
    "Mms": 0.065,                                                       # Masa móvil en kg
    "Vas": 62,                                                          # Volumen de aire equivalente en litros
    "Qts": 0.32,                                                        # Factor de calidad total
    "Qes": 0.34,                                                        # Factor de calidad eléctrico
    "Qms": 4.5,                                                         # Factor de calidad mecánico
    "Re": 5.3,                                                          # Resistencia DC en ohm
    "Bl": 18.1,                                                         # Factor de fuerza en N/A
    "Sd": 0.055,                                                        # Área efectiva del cono en m²
    "Le": 1.5e-3,                                                       # Inductancia de la bobina en H
    "Xmax": 7.5                                                         # Excursión máxima en mm
}
units = {
    "Fs": "Hz",                                                         # Unidad de frecuencia
    "Mms": "kg",                                                        # Unidad de masa
    "Vas": "litros",                                                    # Unidad de volumen
    "Qts": "",                                                          # Factor de calidad sin unidad
    "Qes": "",                                                          # Factor de calidad sin unidad
    "Qms": "",                                                          # Factor de calidad sin unidad
    "Re": "Ω",                                                          # Unidad de resistencia
    "Bl": "N/A",                                                        # Unidad de factor de fuerza
    "Sd": "m²",                                                         # Unidad de área
    "Le": "H",                                                          # Unidad de inductancia
    "Xmax": "mm"                                                        # Unidad de desplazamiento
}

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

def main():
    # Función principal para ejecutar la aplicación SSS.
    # Por defecto ejecuta la versión Qt5, pero puede cambiarse a Tkinter.
    try:
        print("Iniciando aplicación SSS (Qt5)...")                     # Mensaje de inicio de aplicación Qt5
        print("Creando QApplication...")                               # Mensaje de creación de QApplication
        app = QApplication(sys.argv)                                    # Crea la aplicación Qt5
        print("QApplication creada exitosamente")                      # Confirma creación exitosa
        
        print("Creando ventana AppQt...")                              # Mensaje de creación de ventana
        window = AppQt(params, units)                                   # Crea la ventana principal con parámetros
        print("Ventana AppQt creada exitosamente")                     # Confirma creación de ventana
        
        print("Mostrando ventana...")                                  # Mensaje de visualización
        window.show()                                                   # Muestra la ventana en pantalla
        print("Ventana mostrada, iniciando loop de eventos...")        # Confirma inicio del loop
        
        sys.exit(app.exec_())                                           # Ejecuta el loop de eventos y termina al cerrar
    except Exception as e:
        print(f"Error al iniciar aplicación Qt5: {e}")                 # Captura errores de Qt5
        import traceback                                                # Importa traceback para debugging
        traceback.print_exc()                                           # Imprime el stack trace completo
        print("Intentando con aplicación Tkinter...")                  # Mensaje de fallback a Tkinter
        try:
            root = tk.Tk()                                              # Crea ventana raíz de Tkinter
            root.title("SSS - Speaker Simulation System")              # Establece título de la ventana
            app = App(root, params, units)                              # Crea aplicación Tkinter
            root.mainloop()                                             # Ejecuta el loop principal de Tkinter
        except Exception as e2:
            print(f"Error al iniciar aplicación Tkinter: {e2}")        # Captura errores de Tkinter
            import traceback                                            # Importa traceback nuevamente
            traceback.print_exc()                                       # Imprime el stack trace de Tkinter
            print("No se pudo iniciar ninguna aplicación.")            # Mensaje de fallo total
            sys.exit(1)                                                 # Sale con código de error

if __name__ == "__main__":
    main()
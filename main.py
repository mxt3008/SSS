# --------------------------------------------
# main.py
# Script principal para simular y analizar el comportamiento de un parlante.
# --------------------------------------------

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

# --------------------------------------------
# Importar librerías necesarias
# --------------------------------------------

import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from core.driver import Driver
from visualization.plots import plot_all
import sys
from visualization.app import App
from visualization.app_qt5 import AppQt
from PyQt5.QtWidgets import QApplication

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
units = {
    "Fs": "Hz", 
    "Mms": "kg", 
    "Vas": "litros", 
    "Qts": "", 
    "Qes": "", 
    "Qms": "",
    "Re": "Ω", 
    "Bl": "N/A", 
    "Sd": "m²", 
    "Le": "H", 
    "Xmax": "mm"
}

# --------------------------------------------
# Función principal
# --------------------------------------------

def main():
    """
    Función principal para ejecutar la aplicación SSS.
    Por defecto ejecuta la versión Qt5, pero puede cambiarse a Tkinter.
    """
    try:
        # Intentar ejecutar la aplicación Qt5
        print("Iniciando aplicación SSS (Qt5)...")
        print("Creando QApplication...")
        app = QApplication(sys.argv)
        print("QApplication creada exitosamente")
        
        print("Creando ventana AppQt...")
        window = AppQt(params, units)
        print("Ventana AppQt creada exitosamente")
        
        print("Mostrando ventana...")
        window.show()
        print("Ventana mostrada, iniciando loop de eventos...")
        
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error al iniciar aplicación Qt5: {e}")
        import traceback
        traceback.print_exc()
        print("Intentando con aplicación Tkinter...")
        try:
            # Alternativa: ejecutar aplicación Tkinter
            root = tk.Tk()
            root.title("SSS - Speaker Simulation System")
            app = App(root, params, units)
            root.mainloop()
        except Exception as e2:
            print(f"Error al iniciar aplicación Tkinter: {e2}")
            import traceback
            traceback.print_exc()
            print("No se pudo iniciar ninguna aplicación.")
            sys.exit(1)

if __name__ == "__main__":
    main()
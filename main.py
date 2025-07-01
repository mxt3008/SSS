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

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from core.driver import Driver
from visualization.plots import plot_all
import sys
from visualization.app import App

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

if __name__ == "__main__":
    root = tk.Tk()
    root.title("SSS")
    app = App(root, params, units)
    root.mainloop()
    
#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

# Fin del script principal


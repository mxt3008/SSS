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

if __name__ == "__main__":
    from core.bassreflex import BassReflexBox
    from core.driver import Driver
    import matplotlib.pyplot as plt
    import numpy as np

    params = {
        "Fs": 40,
        "Mms": 0.025,
        "Vas": 50,
        "Qts": 0.35,
        "Qes": 0.4,
        "Qms": 4.5,
        "Re": 6.0,
        "Bl": 7.5,
        "Sd": 0.021,
        "Le": 0.5e-3,
        "Xmax": 5.0
    }
    # Usa un puerto más largo y área razonable
    enclosure = BassReflexBox(50, 0.002, 0.20)  # Vb=50L, área ducto=0.002m², largo=0.20m
    driver = Driver(params, enclosure=enclosure)
    freqs = np.logspace(np.log10(10), np.log10(1000), 500)
    Z = np.array([driver.impedance(f) for f in freqs])

    plt.figure()
    plt.semilogx(freqs, np.abs(Z))
    plt.xlabel("Frecuencia [Hz]")
    plt.ylabel("Impedancia [Ohm]")
    plt.title("Bass-reflex: Impedancia eléctrica")
    plt.grid(True, which="both")
    plt.show()

    for f in freqs:
        Za = enclosure.acoustic_load(f, params["Sd"])
        print(f"f={f:.1f} Hz, |Za|={np.abs(Za):.4f} N·s/m")

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

# Fin del script principal


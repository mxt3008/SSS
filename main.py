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

params = {
    "Fs": 52, "Mms": 0.065, "Vas": 62, "Qts": 0.32, "Qes": 0.34, "Qms": 4.5,
    "Re": 5.3, "Bl": 18.1, "Sd": 0.055, "Le": 1.5e-3, "Xmax": 7.5
}
units = {
    "Fs": "Hz", "Mms": "kg", "Vas": "litros", "Qts": "", "Qes": "", "Qms": "",
    "Re": "Ω", "Bl": "N/A", "Sd": "m²", "Le": "H", "Xmax": "mm"
}

class App:
    def __init__(self, root, params, units):
        self.root = root
        self.params = params.copy()
        self.units = units
        self.user_params = params.copy()
        self.driver = None

        # Layout
        self.left_frame = tk.Frame(root, width=350)
        self.left_frame.pack(side="left", fill="y")
        self.right_frame = tk.Frame(root)
        self.right_frame.pack(side="right", fill="both", expand=True)

        # Formulario
        self.entries = {}
        row = 0
        for key in self.params:
            unidad = self.units.get(key, "")
            label = tk.Label(self.left_frame, text=f"{key} [{unidad}]")
            label.grid(row=row, column=0, sticky="w", padx=5, pady=2)
            entry = tk.Entry(self.left_frame, width=12)
            entry.insert(0, str(self.params[key]))
            entry.grid(row=row, column=1, padx=5, pady=2)
            self.entries[key] = entry
            row += 1
        self.submit_btn = tk.Button(self.left_frame, text="Aceptar", command=self.on_submit)
        self.submit_btn.grid(row=row, column=0, columnspan=2, pady=10)

        # Resumen
        self.resumen_text = tk.Text(self.left_frame, width=40, height=15, state="disabled")
        self.resumen_text.grid(row=row+1, column=0, columnspan=2, pady=10)

        # Gráfica
        self.fig, self.axs = plt.subplots(3, 3, figsize=(10, 8))
        self.fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Manejar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_submit(self):
        # Leer parámetros
        for key, entry in self.entries.items():
            val = entry.get()
            try:
                self.user_params[key] = float(val)
            except ValueError:
                self.user_params[key] = self.params[key]
        self.driver = Driver(self.user_params)
        self.update_resumen()
        self.update_plots()

    def update_resumen(self):
        resumen = self.driver.resumen_parametros()
        self.resumen_text.config(state="normal")
        self.resumen_text.delete("1.0", tk.END)
        self.resumen_text.insert(tk.END, resumen)
        self.resumen_text.config(state="disabled")

    def update_plots(self):
        f_max = self.driver.f_max_ka()
        frequencies = np.logspace(np.log10(5), np.log10(f_max), 1000)
        Z_values = np.array([self.driver.impedance(f) for f in frequencies])
        Z_magnitude = np.abs(Z_values)
        Z_phase = np.angle(Z_values, deg=True)
        SPL_total = np.array([self.driver.spl_total(f) for f in frequencies])
        SPL_phase = np.array([self.driver.spl_phase(f) for f in frequencies])
        displacements = np.array([self.driver.displacement(f) for f in frequencies])
        displacements_mm = displacements * 1000
        velocities = np.array([abs(self.driver.velocity(f)) for f in frequencies])
        excursions = velocities / (2 * np.pi * frequencies)
        excursions_mm = excursions * 1000
        excursion_ratio = excursions / self.driver.Xmax

        for ax in self.axs.flatten():
            ax.clear()
        plot_all(
            self.driver, frequencies, Z_magnitude, Z_phase, SPL_total, SPL_phase,
            displacements_mm, velocities, excursions_mm, excursion_ratio, f_max,
            fig=self.fig, axs=self.axs
        )
        self.canvas.draw()

    def on_close(self):
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Simulador de Parlante")
    app = App(root, params, units)
    root.mainloop()
    
#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

# Fin del script principal


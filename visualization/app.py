import tkinter as tk                                                # Importar tkinter para la interfaz gráfica
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg     # Importar el backend de matplotlib para Tkinter
import matplotlib.pyplot as plt                                     # Importar matplotlib para graficar
import numpy as np                                                  # Importar numpy para cálculos numéricos
import sys                                                          # Importar sys para manejar el cierre de la aplicación
from core.driver import Driver                                      # Importar la clase Driver para simular el parlante
from visualization.plots import plot_all                            # Importar la función para graficar todos los datos

class App:                                                          # Clase principal de la aplicación
    def __init__(self, root, params, units):                        # Constructor de la clase
        self.root = root                                            # Guardar la referencia a la ventana principal
        self.params = params.copy()                                 # Copiar los parámetros iniciales
        self.units = units                                          # Guardar las unidades de los parámetros
        self.user_params = params.copy()                            # Copiar los parámetros para el usuario
        self.driver = None                                          # Inicializar el driver como None

        # PanedWindow horizontal: izquierda (panel izquierdo) y derecha (gráfica)
        self.h_paned = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        self.h_paned.pack(fill="both", expand=True)

        # PanedWindow vertical para el panel izquierdo (formulario, resumen, checkboxes)
        self.v_paned = tk.PanedWindow(self.h_paned, orient=tk.VERTICAL, sashrelief=tk.RAISED)
        self.h_paned.add(self.v_paned, minsize=350)

        # Frame para formulario (arriba)
        self.form_frame = tk.Frame(self.v_paned)
        self.v_paned.add(self.form_frame, minsize=100)

        self.entries = {}
        row = 0
        for key in self.params:
            unidad = self.units.get(key, "")
            label = tk.Label(self.form_frame, text=f"{key} [{unidad}]")
            label.grid(row=row, column=0, sticky="w", padx=5, pady=2)
            entry = tk.Entry(self.form_frame, width=12)
            entry.insert(0, str(self.params[key]))
            entry.grid(row=row, column=1, padx=5, pady=2)
            self.entries[key] = entry
            row += 1
        self.submit_btn = tk.Button(self.form_frame, text="Aceptar", command=self.on_submit)
        self.submit_btn.grid(row=row, column=0, columnspan=2, pady=10)

        # Frame para resumen (abajo)
        self.resumen_frame = tk.Frame(self.v_paned)
        self.v_paned.add(self.resumen_frame, minsize=100)

        # Scrollbar para el resumen
        self.resumen_text = tk.Text(self.resumen_frame, width=40, state="disabled", wrap="word")
        self.resumen_text.pack(side="left", fill="both", expand=True)
        self.scrollbar = tk.Scrollbar(self.resumen_frame, command=self.resumen_text.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.resumen_text.config(yscrollcommand=self.scrollbar.set)

        # Frame para checkboxes de curvas (abajo del resumen)
        self.checkbox_frame = tk.LabelFrame(self.v_paned, text="Curvas simuladas")
        self.v_paned.add(self.checkbox_frame, minsize=60)

        # Frame derecho (gráfica)
        self.right_frame = tk.Frame(self.h_paned)
        self.h_paned.add(self.right_frame)

        # Gráfica
        self.fig, self.axs = plt.subplots(3, 3, figsize=(10, 8))
        self.fig.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Maximizar subgráfica al doble clic
        self.fig.canvas.mpl_connect("button_press_event", self.on_subplot_click)

        # Manejar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.plot_count = 0
        self.plot_lines = []  # Lista de listas de líneas por simulación
        self.check_vars = []  # Variables de los checkboxes
        self.checkboxes = []  # Referencias a los checkboxes

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
        # Alternar solo el estilo de línea
        linestyles = ["-", "--", "-.", ":"]
        linestyle = linestyles[self.plot_count % len(linestyles)]

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

        # Graficar y obtener las líneas de esta simulación
        lines = plot_all(
            self.driver, frequencies, Z_magnitude, Z_phase, SPL_total, SPL_phase,
            displacements_mm, velocities, excursions_mm, excursion_ratio, f_max,
            fig=self.fig, axs=self.axs, linestyle=linestyle
        )
        self.canvas.draw()

        # Guardar las líneas para controlarlas con los checkboxes
        self.plot_lines.append(lines)
        self.plot_count += 1

        # Crear checkbox para esta simulación
        var = tk.BooleanVar(value=True)
        label = f"Simulación {self.plot_count} ({linestyle})"
        cb = tk.Checkbutton(self.checkbox_frame, text=label, variable=var,
                            command=lambda idx=len(self.plot_lines)-1: self.toggle_lines(idx))
        cb.pack(anchor="w")
        self.check_vars.append(var)
        self.checkboxes.append(cb)

    def toggle_lines(self, idx):
        visible = self.check_vars[idx].get()
        for line in self.plot_lines[idx]:
            line.set_visible(visible)
        self.canvas.draw()

    def on_subplot_click(self, event):
        if event.dblclick:
            self.maximize_subplot(event)

    def maximize_subplot(self, event):
        ax = event.inaxes
        if ax is None:
            return
        fig = plt.figure(figsize=(8, 6))
        new_ax = fig.add_subplot(111)
        for line in ax.get_lines():
            new_ax.plot(line.get_xdata(), line.get_ydata(),
                        color=line.get_color(),
                        linestyle=line.get_linestyle(),
                        label=line.get_label(),
                        visible=line.get_visible())
        new_ax.set_title(ax.get_title())
        new_ax.set_xlabel(ax.get_xlabel())
        new_ax.set_ylabel(ax.get_ylabel())
        new_ax.legend()
        fig.tight_layout()
        fig.show()

    def on_close(self):
        self.root.destroy()
        sys.exit(0)
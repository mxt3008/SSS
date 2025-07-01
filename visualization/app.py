import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import LogLocator, ScalarFormatter, MultipleLocator
import matplotlib.pyplot as plt
import numpy as np
import sys
from core.driver import Driver
from visualization.plots import plot_all


class App:
    def __init__(self, root, params, units):
        self.root = root
        self.params = params.copy()
        self.units = units
        self.user_params = params.copy()
        self.driver = None
        self.simulated_params = set()

        self.check_vars = []
        self.checkboxes = []
        self.plot_lines = []
        self.plot_count = 0

        # --- Ventana principal en proporción 16:9 ---
        self.root.geometry("1600x900")
        self.root.minsize(960, 540)

        # --- Barra de herramientas superior ---
        self.toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        self.toolbar.pack(side="top", fill="x")

        self.sim_btn = tk.Button(self.toolbar, text="Simular", command=self.on_submit)
        self.sim_btn.pack(side="left", padx=2, pady=2)

        self.export_btn = tk.Button(self.toolbar, text="Exportar...", command=self.export_txt)
        self.export_btn.pack(side="left", padx=2, pady=2)

        # --- Botón para mostrar/ocultar leyendas ---
        self.show_legends = False
        self.legend_btn = tk.Button(self.toolbar, text="Mostrar leyendas", command=self.toggle_legends)
        self.legend_btn.pack(side="left", padx=2, pady=2)

        # --- Botón para mostrar/ocultar cursor grid ---
        self.enable_grid_cursor = False
        self.grid_cursor = None
        self.cursor_btn = tk.Button(self.toolbar, text="Mostrar cursor grid", command=self.toggle_grid_cursor)
        self.cursor_btn.pack(side="left", padx=2, pady=2)

        # --- PanedWindow horizontal: izquierda y derecha ---
        self.h_paned = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        self.h_paned.pack(fill="both", expand=True)

        # --- PanedWindow vertical para el panel izquierdo ---
        self.v_paned = tk.PanedWindow(self.h_paned, orient=tk.VERTICAL, sashrelief=tk.RAISED)
        self.h_paned.add(self.v_paned, minsize=350)

        # --- Frame para formulario (arriba) ---
        self.form_frame = tk.LabelFrame(self.v_paned, text="Selección e ingreso de parámetros")
        self.v_paned.add(self.form_frame, minsize=180)

        tk.Label(self.form_frame, text="Información del Driver", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5, 0))  # <-- menos espacio abajo

        # --- Canvas y Scrollbar para el formulario ---
        self.form_canvas = tk.Canvas(self.form_frame, borderwidth=0, highlightthickness=0)
        self.form_canvas.pack(side="left", fill="both", expand=True)
        self.form_scrollbar = tk.Scrollbar(self.form_frame, orient="vertical", command=self.form_canvas.yview)
        self.form_scrollbar.pack(side="right", fill="y")
        self.form_canvas.configure(yscrollcommand=self.form_scrollbar.set)

        self.form_container = tk.Frame(self.form_canvas)
        self.form_window_id = self.form_canvas.create_window((0, 0), window=self.form_container, anchor="nw")

        def _on_form_configure(event):
            self.form_canvas.configure(scrollregion=self.form_canvas.bbox("all"))
        self.form_container.bind("<Configure>", _on_form_configure)

        def _on_form_canvas_configure(event):
            self.form_canvas.itemconfig(self.form_window_id, width=event.width)
        self.form_canvas.bind("<Configure>", _on_form_canvas_configure)

        # --- Entradas del formulario dentro de form_container ---
        self.entries = {}
        row = 0
        # Etiqueta encima del Entry para el nombre del driver
        tk.Label(self.form_container, text="Nombre del driver:").grid(row=row, column=0, columnspan=3, sticky="w", padx=5, pady=(5, 0))
        row += 1
        self.name_var = tk.StringVar()
        tk.Entry(self.form_container, textvariable=self.name_var, width=16).grid(row=row, column=0, columnspan=3, padx=5, pady=(0, 4), sticky="w")
        row += 1

        # Subtítulo antes de los parámetros
        tk.Label(self.form_container, text="Parámetros:", font=("Arial", 10, "bold")).grid(
            row=row, column=0, columnspan=3, sticky="w", padx=5, pady=(0, 4)
        )
        row += 1

        for key in self.params:
            unidad = self.units.get(key, "")
            label = tk.Label(self.form_container, text=key)
            label.grid(row=row, column=0, sticky="e", padx=5, pady=2)
            entry = tk.Entry(self.form_container, width=8)
            entry.insert(0, str(self.params[key]))
            entry.grid(row=row, column=1, padx=5, pady=2, sticky="w")
            unit_label = tk.Label(self.form_container, text=f"[{unidad}]" if unidad else "")
            unit_label.grid(row=row, column=2, sticky="w", padx=(2, 0), pady=2)
            self.entries[key] = entry
            row += 1

        self.form_container.grid_columnconfigure(1, weight=0)  # No expandir

        # --- Frame para resumen (abajo del formulario) ---
        self.resumen_frame = tk.LabelFrame(self.v_paned, text="Resumen de parámetros EMA - TS")
        self.v_paned.add(self.resumen_frame, minsize=120)
        tk.Label(self.resumen_frame, text="Resumen", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5, 0))

        self.resumen_text = tk.Text(self.resumen_frame, width=40, state="disabled", wrap="word", height=8)
        self.resumen_text.pack(side="left", fill="both", expand=True)
        self.scrollbar = tk.Scrollbar(self.resumen_frame, command=self.resumen_text.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.resumen_text.config(yscrollcommand=self.scrollbar.set)

        # --- Frame para checkboxes de curvas (abajo del resumen) ---
        self.checkbox_frame = tk.LabelFrame(self.v_paned, text="Curvas simuladas")
        self.v_paned.add(self.checkbox_frame, minsize=50)

        # --- Frame intermedio con altura fija ---
        self.checkbox_area = tk.Frame(self.checkbox_frame)
        self.checkbox_area.pack(fill="both", expand=True)
        self.checkbox_area.pack_propagate(False)

        # --- Canvas y Scrollbar dentro del frame intermedio ---
        self.checkbox_canvas = tk.Canvas(self.checkbox_area, borderwidth=0, highlightthickness=0)
        self.checkbox_canvas.pack(side="left", fill="both", expand=True)
        self.checkbox_scrollbar = tk.Scrollbar(self.checkbox_area, orient="vertical", command=self.checkbox_canvas.yview)
        self.checkbox_scrollbar.pack(side="right", fill="y")
        self.checkbox_canvas.configure(yscrollcommand=self.checkbox_scrollbar.set)

        self.checkboxes_container = tk.Frame(self.checkbox_canvas)
        self.window_id = self.checkbox_canvas.create_window((0, 0), window=self.checkboxes_container, anchor="nw")

        def _on_frame_configure(event):
            self.checkbox_canvas.configure(scrollregion=self.checkbox_canvas.bbox("all"))
        self.checkboxes_container.bind("<Configure>", _on_frame_configure)

        def _on_canvas_configure(event):
            self.checkbox_canvas.itemconfig(self.window_id, width=event.width)
        self.checkbox_canvas.bind("<Configure>", _on_canvas_configure)

        # Ajusta el alto del canvas al redimensionar el área
        def _on_area_configure(event):
            self.checkbox_canvas.config(height=event.height)
        self.checkbox_area.bind("<Configure>", _on_area_configure)

        header_frame = tk.Frame(self.checkboxes_container)
        header_frame.pack(fill="x", pady=(5, 0))
        tk.Label(header_frame, text="Selección de Gráficas", font=("Arial", 10, "bold")).pack(side="left", anchor="w")

        # --- Frame derecho (gráfica) ---
        self.right_frame = tk.Frame(self.h_paned)
        self.h_paned.add(self.right_frame)

        self.plots_title = tk.Label(self.right_frame, text="Gráficas de Simulación", font=("Arial", 10, "bold"))
        self.plots_title.pack(anchor="center", pady=(5, 0))

        self.fig = None
        self.axs = None
        self.canvas = None

        # Escalado dinámico de paneles al redimensionar
        self.root.bind("<Configure>", self.on_resize)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Fijar proporción horizontal 30% (izquierda) y 70% (derecha) al inicio
        self.root.update_idletasks()
        total_width = self.root.winfo_width()
        ancho_izquierdo = int(total_width * 0.25)  # 30%
        try:
            self.h_paned.sash_place(0, ancho_izquierdo, 0)
        except Exception:
            pass

    def on_resize(self, event):
        if event.widget is not self.root:
            return
        if hasattr(self, "_resize_after_id"):
            self.root.after_cancel(self._resize_after_id)
        self._resize_after_id = self.root.after(150, self._do_resize)

    def _do_resize(self):
        total_height = self.root.winfo_height()
        form_h = int(total_height * 0.45)
        resumen_h = int(total_height * 0.35)
        checkbox_h = max(50, int(total_height * 0.20))
        try:
            self.v_paned.sash_place(0, 0, form_h)
            self.v_paned.sash_place(1, 0, form_h + resumen_h)
        except Exception:
            pass

    def on_submit(self):
        # Leer parámetros
        for key, entry in self.entries.items():
            val = entry.get()
            try:
                self.user_params[key] = float(val)
            except ValueError:
                self.user_params[key] = self.params[key]
        # Crea una tupla ordenada de los parámetros para comparar
        param_tuple = tuple((k, self.user_params[k]) for k in sorted(self.user_params))
        if param_tuple in self.simulated_params:
            messagebox.showerror("Error", "Ya existe una simulación con estos parámetros. Modifica algún valor para simular un driver diferente.")
            return
        self.simulated_params.add(param_tuple)
        self.driver = Driver(self.user_params)
        self.update_resumen()
        self.update_plots()

    def update_resumen(self):
        resumen = self.driver.resumen_parametros()
        self.resumen_text.config(state="normal")
        self.resumen_text.delete("1.0", tk.END)
        self.resumen_text.insert(tk.END, resumen)
        self.resumen_text.config(state="disabled")

    def export_txt(self):
        if self.driver is None:
            messagebox.showerror("Error", "Primero realiza una simulación antes de exportar.")
            return
        nombre = self.name_var.get().strip() or "driver"
        resumen = self.driver.resumen_parametros()
        params_str = "Parámetros del driver:\n"
        for k, v in self.user_params.items():
            unidad = self.units.get(k, "")
            params_str += f"{k}: {v} {unidad}\n"
        contenido = f"Nombre: {nombre}\n\n{params_str}\nResumen:\n{resumen}"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivo de texto", "*.txt")],
            initialfile=f"{nombre}_resumen.txt"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(contenido)
                messagebox.showinfo("Exportación exitosa", f"Archivo guardado en:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

    def toggle_legends(self):
        self.show_legends = not self.show_legends
        # Cambia el texto del botón
        self.legend_btn.config(text="Ocultar leyendas" if self.show_legends else "Mostrar leyendas")
        # Mostrar u ocultar leyendas en todos los ejes
        if self.axs is not None:
            for ax in self.axs.flatten():
                leg = ax.get_legend()
                if leg:
                    leg.set_visible(self.show_legends)
            if self.canvas:
                self.canvas.draw()

    def toggle_grid_cursor(self):
        self.enable_grid_cursor = not self.enable_grid_cursor
        self.cursor_btn.config(
            text="Ocultar cursor grid" if self.enable_grid_cursor else "Mostrar cursor grid"
        )
        self.update_plots()

    def update_plots(self):
        import matplotlib
        import matplotlib.pyplot as plt

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

        nombre_driver = self.name_var.get().strip() or f"Simulación {self.plot_count+1}"

        # Solo crea la figura y canvas la primera vez
        if self.fig is None or self.axs is None or self.canvas is None:
            lines, cursor = plot_all(
                self.driver, frequencies, Z_magnitude, Z_phase, SPL_total, SPL_phase,
                displacements_mm, velocities, excursions_mm, excursion_ratio, f_max,
                fig=None, axs=None, linestyle=linestyle, label=nombre_driver,
                show_legend=self.show_legends,
                enable_cursor=self.enable_grid_cursor,
                grid_cursor=self.grid_cursor
            )
            self.fig = plt.gcf()
            self.axs = np.array(self.fig.axes)
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
            self.fig.canvas.mpl_connect("button_press_event", self.on_subplot_click)
            self.grid_cursor = cursor
        else:
            # Agrega nuevas líneas a los ejes existentes
            lines, cursor = plot_all(
                self.driver, frequencies, Z_magnitude, Z_phase, SPL_total, SPL_phase,
                displacements_mm, velocities, excursions_mm, excursion_ratio, f_max,
                fig=self.fig, axs=self.axs, linestyle=linestyle, label=nombre_driver,
                show_legend=self.show_legends,
                enable_cursor=self.enable_grid_cursor,
                grid_cursor=self.grid_cursor
            )
            self.grid_cursor = cursor

        self.canvas.draw()

        # Asegura que las leyendas estén ocultas o visibles según el estado del botón,
        # incluso después de agregar nuevas gráficas
        if self.axs is not None:
            for ax in self.axs.flatten():
                leg = ax.get_legend()
                if leg:
                    leg.set_visible(self.show_legends)
            if self.canvas:
                self.canvas.draw()

        self.plot_lines.append(lines)
        self.plot_count += 1

        for cb in self.checkboxes:
            cb.destroy()
        self.check_vars = []
        self.checkboxes = []
        for idx, lineset in enumerate(self.plot_lines):
            var = tk.BooleanVar(value=True)
            label = f"Simulación {idx+1} ({linestyles[idx % len(linestyles)]})"
            cb = tk.Checkbutton(self.checkboxes_container, text=label, variable=var,
                                command=lambda idx=idx: self.toggle_lines(idx))
            cb.pack(fill="x", padx=4, pady=2)
            self.check_vars.append(var)
            self.checkboxes.append(cb)

        self.checkboxes_container.update_idletasks()
        self.checkbox_canvas.configure(scrollregion=self.checkbox_canvas.bbox("all"))

    def toggle_lines(self, idx):
        visible = self.check_vars[idx].get()
        for line in self.plot_lines[idx]:
            line.set_visible(visible)
        self.canvas.draw()

    def on_subplot_click(self, event):
        if event.dblclick:
            self.maximize_subplot(event)

    def maximize_subplot(self, event):
        import mplcursors
        ax = event.inaxes
        if ax is None:
            return
        fig = plt.figure(figsize=(8, 6))
        new_ax = fig.add_subplot(111)

        # Copiar líneas del eje principal
        for line in ax.get_lines():
            new_ax.plot(line.get_xdata(), line.get_ydata(),
                        color=line.get_color(),
                        linestyle=line.get_linestyle(),
                        label=line.get_label(),
                        visible=line.get_visible())

        # Si hay eje secundario (twinx), copiar también sus líneas
        twin_ax = None
        for other_ax in ax.figure.axes:
            if other_ax is not ax and hasattr(other_ax, 'get_shared_x_axes') and ax.get_shared_x_axes() == other_ax.get_shared_x_axes():
                twin_ax = other_ax
                break

        if twin_ax:
            new_twin = new_ax.twinx()
            for line in twin_ax.get_lines():
                new_twin.plot(line.get_xdata(), line.get_ydata(),
                              color=line.get_color(),
                              linestyle=line.get_linestyle(),
                              label=line.get_label(),
                              visible=line.get_visible())
            new_twin.set_ylabel(twin_ax.get_ylabel(), fontsize=9)
            new_twin.legend(fontsize=9, loc="upper right")
        else:
            new_ax.legend(fontsize=9)

        # Título y etiquetas
        title = ax.get_title() or "Gráfica"
        new_ax.set_title(title, fontsize=10, fontweight='bold')
        new_ax.set_xlabel(ax.get_xlabel(), fontsize=9)
        new_ax.set_ylabel(ax.get_ylabel(), fontsize=9)
        new_ax.grid(True, which="both")
        new_ax.set_xscale('log')
        new_ax.xaxis.set_major_locator(LogLocator(base=10.0, numticks=10))
        new_ax.xaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10)*.1, numticks=10))
        new_ax.xaxis.set_major_formatter(ScalarFormatter())
        new_ax.tick_params(axis='both', labelsize=8)
        if "SPL" in new_ax.get_title():
            new_ax.yaxis.set_major_locator(MultipleLocator(10))

        cursor = mplcursors.cursor(new_ax.get_lines(), hover=True)
        def cursor_fmt(sel):
            x = sel.target[0]
            y = sel.target[1]
            x_label = f"{x/1000:.1f}k" if x >= 1000 else f"{x:.0f}"
            label = sel.artist.get_label()
            if "∠Z" in label or "Phase" in label or "Fase" in label:
                y_unit = "°"
            elif "|Z|" in label:
                y_unit = "Ω"
            elif "SPL" in label:
                y_unit = "dB"
            elif "Desplazamiento" in label:
                y_unit = "mm"
            elif "Velocidad" in label:
                y_unit = "m/s"
            elif "Excursión/Xmax" in label:
                y_unit = "(ratio)"
            elif "Excursión" in label:
                y_unit = "mm"
            else:
                y_unit = ""
            sel.annotation.set_text(f"X: {x_label} Hz\nY: {y:.2f} {y_unit}")
        cursor.connect("add", cursor_fmt)
        fig.tight_layout()
        fig.show()

    def on_close(self):
        self.root.destroy()
        sys.exit(0)
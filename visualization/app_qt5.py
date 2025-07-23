import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLabel, QLineEdit, QComboBox, QFormLayout, QCheckBox, QTextEdit, QFileDialog, QScrollArea, QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from core.driver import Driver
from visualization.plots import plot_all

class AppQt(QMainWindow):
    def __init__(self, params, units):
        super().__init__()
        self.setWindowTitle("SSS - Qt5")
        self.resize(1600, 900)

        self.params = params.copy()
        self.units = units
        self.user_params = params.copy()
        self.sim_names = []
        self.plot_lines = []
        self.plot_count = 0
        self.show_legends = False
        self.enable_grid_cursor = False
        self.grid_cursor = None

        # --- Layout principal ---
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # --- Panel izquierdo: formulario y controles ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        main_layout.addWidget(left_panel, 2)

        # --- Formulario de parámetros ---
        form_group = QGroupBox("Parámetros del Driver y Recinto")
        form_layout = QFormLayout(form_group)
        left_layout.addWidget(form_group)

        self.entries = {}
        for key in self.params:
            entry = QLineEdit(str(self.params[key]))
            self.entries[key] = entry
            unidad = self.units.get(key, "")
            form_layout.addRow(f"{key} [{unidad}]", entry)

        # --- Recinto ---
        self.enclosure_type_combo = QComboBox()
        self.enclosure_type_combo.addItems([
            "Infinite Baffle", "Caja Sellada", "Bass-reflex", "Bandpass Isobárico"
        ])
        form_layout.addRow("Tipo de recinto:", self.enclosure_type_combo)

        self.vb_entry = QLineEdit("20")
        form_layout.addRow("Vb [L]:", self.vb_entry)

        self.area_port_entry = QLineEdit("0.01")
        self.length_port_entry = QLineEdit("0.10")
        form_layout.addRow("Área ducto [m²]:", self.area_port_entry)
        form_layout.addRow("Largo ducto [m]:", self.length_port_entry)

        # --- Modelo de radiación frontal ---
        self.radiation_model_combo = QComboBox()
        self.radiation_model_combo.addItems(["baffled", "unbaffled"])
        form_layout.addRow("Modelo de radiación:", self.radiation_model_combo)

        # --- Nombre de simulación ---
        self.name_entry = QLineEdit()
        form_layout.addRow("Nombre simulación:", self.name_entry)

        # --- Botones ---
        btn_layout = QHBoxLayout()
        self.sim_btn = QPushButton("Simular")
        self.sim_btn.clicked.connect(self.on_submit)
        btn_layout.addWidget(self.sim_btn)

        self.export_btn = QPushButton("Exportar...")
        self.export_btn.clicked.connect(self.export_txt)
        btn_layout.addWidget(self.export_btn)

        self.legend_btn = QPushButton("Mostrar leyendas")
        self.legend_btn.setCheckable(True)
        self.legend_btn.clicked.connect(self.toggle_legends)
        btn_layout.addWidget(self.legend_btn)

        self.cursor_btn = QPushButton("Mostrar cursor grid")
        self.cursor_btn.setCheckable(True)
        self.cursor_btn.clicked.connect(self.toggle_grid_cursor)
        btn_layout.addWidget(self.cursor_btn)

        left_layout.addLayout(btn_layout)

        # --- Resumen ---
        self.resumen_text = QTextEdit()
        self.resumen_text.setReadOnly(True)
        left_layout.addWidget(self.resumen_text, 1)

        # --- Checkboxes de simulaciones ---
        self.checkbox_area = QWidget()
        self.checkbox_layout = QVBoxLayout(self.checkbox_area)
        left_layout.addWidget(self.checkbox_area)
        self.checkboxes = []
        self.check_vars = []

        # --- Panel derecho: pestañas de gráficas ---
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs, 5)

        # Pestaña principal: grid 3x3
        self.grid_tab = QWidget()
        self.grid_layout = QVBoxLayout(self.grid_tab)
        self.tabs.addTab(self.grid_tab, "Grid 3x3")

        # Pestañas individuales
        self.single_plot_tabs = []
        for i in range(9):
            tab = QWidget()
            layout = QVBoxLayout(tab)
            self.tabs.addTab(tab, f"Gráfica {i+1}")
            self.single_plot_tabs.append((tab, layout))

        # --- Estado de la figura ---
        self.fig = None
        self.axs = None
        self.canvas = None

        # --- Filas de los campos de recinto ---
        self.vb_row = form_layout.rowCount()
        self.area_row = self.vb_row + 1
        self.length_row = self.vb_row + 2

        def update_enclosure_fields():
            tipo = self.enclosure_type_combo.currentText()
            
            # Campos básicos de volumen (para todas las cajas excepto Infinite Baffle)
            vb_visible = tipo != "Infinite Baffle"
            form_layout.labelForField(self.vb_entry).setVisible(vb_visible)
            self.vb_entry.setVisible(vb_visible)
            
            # Campos de Bass-reflex
            bassreflex_visible = tipo == "Bass-reflex"
            form_layout.labelForField(self.area_port_entry).setVisible(bassreflex_visible)
            self.area_port_entry.setVisible(bassreflex_visible)
            form_layout.labelForField(self.length_port_entry).setVisible(bassreflex_visible)
            self.length_port_entry.setVisible(bassreflex_visible)
            
            # Campos específicos de Bandpass Isobárico
            bandpass_visible = tipo == "Bandpass Isobárico"
            
            # Volúmenes para bandpass
            form_layout.labelForField(self.vb_front_entry).setVisible(bandpass_visible)
            self.vb_front_entry.setVisible(bandpass_visible)
            form_layout.labelForField(self.vab_entry).setVisible(bandpass_visible)
            self.vab_entry.setVisible(bandpass_visible)
            
            # Ductos para bandpass
            form_layout.labelForField(self.fp_entry).setVisible(bandpass_visible)
            self.fp_entry.setVisible(bandpass_visible)
            form_layout.labelForField(self.dd_entry).setVisible(bandpass_visible)
            self.dd_entry.setVisible(bandpass_visible)
            form_layout.labelForField(self.dp_entry).setVisible(bandpass_visible)
            self.dp_entry.setVisible(bandpass_visible)
            form_layout.labelForField(self.lp_entry).setVisible(bandpass_visible)
            self.lp_entry.setVisible(bandpass_visible)
            
            # Solo parámetros específicos para sistema isobárico (no duplicar los del driver)
            form_layout.labelForField(self.lvc_entry).setVisible(bandpass_visible)
            self.lvc_entry.setVisible(bandpass_visible)
            form_layout.labelForField(self.mmd_entry).setVisible(bandpass_visible)
            self.mmd_entry.setVisible(bandpass_visible)

        # Conectar la función y habilitar la funcionalidad
        self.enclosure_type_combo.currentIndexChanged.connect(update_enclosure_fields)

        self.simulation_history = []

        # --- Campos adicionales para Bandpass Isobárico ---
        # Volúmenes
        self.vb_front_entry = QLineEdit("15")  # Volumen cámara frontal
        form_layout.addRow("Volumen cámara frontal Vf [L]:", self.vb_front_entry)
        self.vab_entry = QLineEdit("25")  # Volumen cámara trasera 
        form_layout.addRow("Volumen cámara trasera Vab [L]:", self.vab_entry)
        
        # Ductos
        self.fp_entry = QLineEdit("45")
        form_layout.addRow("Frecuencia de sintonía fp [Hz]:", self.fp_entry)
        self.dd_entry = QLineEdit("0.20")
        form_layout.addRow("Diámetro diafragma dd [m]:", self.dd_entry)
        self.dp_entry = QLineEdit("0.10")
        form_layout.addRow("Diámetro puerto dp [m]:", self.dp_entry)
        self.lp_entry = QLineEdit("0.15")
        form_layout.addRow("Longitud puerto Lp [m]:", self.lp_entry)

        # Parámetros específicos para bandpass isobárico
        self.lvc_entry = QLineEdit("0.1")
        form_layout.addRow("Lvc [mH]:", self.lvc_entry)
        self.mmd_entry = QLineEdit("0.015")
        form_layout.addRow("Mmd [kg]:", self.mmd_entry)

        # Inicializar la visibilidad de los campos
        update_enclosure_fields()

    def on_submit(self):
        # Leer parámetros
        for key, entry in self.entries.items():
            try:
                self.user_params[key] = float(entry.text())
            except ValueError:
                self.user_params[key] = self.params[key]

        enclosure_type = self.enclosure_type_combo.currentText()
        try:
            vb_litros = float(self.vb_entry.text())
        except ValueError:
            vb_litros = 20.0

        # Leer ducto solo si es Bass-reflex
        if enclosure_type == "Bass-reflex":
            try:
                area_ducto = float(self.area_port_entry.text())
            except ValueError:
                area_ducto = 0.01
            try:
                largo_ducto = float(self.length_port_entry.text())
            except ValueError:
                largo_ducto = 0.10
            from core.bassreflex import BassReflexBox
            enclosure = BassReflexBox(vb_litros, area_ducto, largo_ducto)
        elif enclosure_type == "Caja Sellada":
            from core.sealed import SealedBox
            enclosure = SealedBox(vb_litros)
        elif enclosure_type == "Bandpass Isobárico":
            # Usar la clase BandpassIsobaricBox
            try:
                vab_litros = float(self.vab_entry.text())
            except ValueError:
                vab_litros = 25.0
                
            from core.bandpass_isobaric import BandpassIsobaricBox
            params_bandpass = {
                'rho0': 1.2,
                'c0': 344,
                'V0': 2.83,
                'B': 0.8333,
                'Re': self.user_params['Re'],  # Usar parámetros originales del driver
                'Red': 3.77,
                'Qes': self.user_params['Qes'],
                'Qms': self.user_params['Qms'],
                'fs': self.user_params['Fs'],
                'Lvc': float(self.lvc_entry.text()) / 1000,  # convertir mH a H
                'S': self.user_params['Sd'],
                'Vab': vab_litros / 1000,  # convertir a m³
                'Vf': float(self.vb_front_entry.text()) / 1000,  # convertir a m³
                'fp': float(self.fp_entry.text()),
                'dd': float(self.dd_entry.text()),
                'dp': float(self.dp_entry.text()),
                'Lp': float(self.lp_entry.text()),
                'BL': self.user_params['Bl'],
                'Mmd': float(self.mmd_entry.text()),
            }
            enclosure = BandpassIsobaricBox(params_bandpass)
            
            # Mostrar mensaje informativo
            QMessageBox.information(self, "Bandpass Isobárico", 
                                  "Bandpass Isobárico configurado correctamente.\n"
                                  "Volúmenes configurados:\n"
                                  f"- Cámara frontal: {self.vb_front_entry.text()} L\n"
                                  f"- Cámara trasera: {self.vab_entry.text()} L\n"
                                  f"- Frecuencia de sintonía: {self.fp_entry.text()} Hz")
        else:
            enclosure = None

        radiation_model = self.radiation_model_combo.currentText()
        nombre_driver = self.name_entry.text().strip() or f"Simulación {self.plot_count+1}"
        self.sim_names.append(nombre_driver)

        # Crear driver
        sim_key = (
            tuple(sorted(self.user_params.items())),
            self.enclosure_type_combo.currentText(),
            self.vb_entry.text(),
            self.area_port_entry.text(),
            self.length_port_entry.text(),
            self.radiation_model_combo.currentText()
        )
        if sim_key in self.simulation_history:
            QMessageBox.warning(self, "Simulación duplicada", "Ya existe una simulación con estos parámetros.")
            return
        self.simulation_history.append(sim_key)

        # Crear driver o sistema bandpass
        if enclosure_type == "Bandpass Isobárico":
            # Para bandpass isobárico, usamos su propia simulación
            self.bandpass_system = enclosure
            self.driver = None  # No usar Driver normal
            # Crear resumen personalizado para bandpass
            self.resumen_text.setPlainText(f"""Sistema Bandpass Isobárico configurado:

=== Configuración de Cámara ===
Volumen cámara frontal: {self.vb_front_entry.text()} L
Volumen cámara trasera: {self.vab_entry.text()} L

=== Configuración de Puerto ===
Frecuencia de sintonía: {self.fp_entry.text()} Hz
Diámetro diafragma: {self.dd_entry.text()} m
Diámetro puerto: {self.dp_entry.text()} m
Longitud puerto: {self.lp_entry.text()} m

=== Parámetros Isobáricos ===
Inductancia de bobina: {self.lvc_entry.text()} mH
Masa del diafragma: {self.mmd_entry.text()} kg

=== Parámetros del Driver (desde campos principales) ===
Re = {self.user_params['Re']} Ω
Qes = {self.user_params['Qes']}
Qms = {self.user_params['Qms']}
Fs = {self.user_params['Fs']} Hz
Bl = {self.user_params['Bl']} N/A
Sd = {self.user_params['Sd']} m²

Nota: Los parámetros del driver se toman de los campos principales,
no hay duplicación de parámetros.""")
        else:
            # Para otros tipos, usar Driver normal
            self.driver = Driver(self.user_params, enclosure=enclosure, radiation_model=radiation_model)
            self.bandpass_system = None
            self.update_resumen()
            
        self.update_plots()

    def update_resumen(self):
        if hasattr(self, 'driver') and self.driver is not None:
            resumen = self.driver.resumen_parametros()
            self.resumen_text.setPlainText(resumen)
        # Para bandpass, el resumen ya se configuró en on_submit()

    def export_txt(self):
        if not hasattr(self, "driver") or self.driver is None:
            return
        nombre = self.name_entry.text().strip() or "driver"
        resumen = self.driver.resumen_parametros()
        params_str = "Parámetros del driver:\n"
        for k, v in self.user_params.items():
            unidad = self.units.get(k, "")
            params_str += f"{k}: {v} {unidad}\n"
        contenido = f"Nombre: {nombre}\n\n{params_str}\nResumen:\n{resumen}"
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar resumen", f"{nombre}_resumen.txt", "Archivo de texto (*.txt)")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(contenido)

    def toggle_legends(self):
        self.show_legends = not self.show_legends
        # Solo muestra/oculta las leyendas, NO generes una nueva simulación
        if self.fig is not None and self.axs is not None:
            for ax in self.axs:
                legend = ax.get_legend()
                if legend:
                    legend.set_visible(self.show_legends)
            if self.canvas is not None:
                self.canvas.draw()
        # También actualiza la ventana maximizada si existe
        import matplotlib._pylab_helpers
        try:
            from visualization.plots import toggle_legends_on_figure
            for manager in matplotlib._pylab_helpers.Gcf.get_all_fig_managers():
                fig = manager.canvas.figure
                toggle_legends_on_figure(fig, self.show_legends)
        except Exception:
            pass

        # También actualiza las leyendas en las pestañas individuales si quieres:
        for i, (tab, layout) in enumerate(self.single_plot_tabs):
            for j in range(layout.count()):
                widget = layout.itemAt(j).widget()
                if hasattr(widget, "figure"):
                    for ax in widget.figure.axes:
                        legend = ax.get_legend()
                        if legend:
                            legend.set_visible(self.show_legends)
                    widget.draw()

    def toggle_grid_cursor(self):
        self.enable_grid_cursor = not self.enable_grid_cursor
        # Solo activa/desactiva el cursor, NO generes una nueva simulación
        if self.enable_grid_cursor:
            # Activa el cursor grid en la figura actual
            import mplcursors
            if hasattr(self, "grid_cursor") and self.grid_cursor is not None:
                try:
                    self.grid_cursor.remove()
                except Exception:
                    pass
            all_lines = []
            for ax in self.axs:
                all_lines.extend(ax.get_lines())
                for other in ax.figure.axes:
                    if other is not ax and getattr(other, "_sharex", None) is ax:
                        all_lines.extend(other.get_lines())
            self.grid_cursor = mplcursors.cursor(all_lines, hover=True)
            # Puedes definir aquí el formato del cursor si lo deseas
        else:
            # Desactiva el cursor grid
            if hasattr(self, "grid_cursor") and self.grid_cursor is not None:
                try:
                    self.grid_cursor.remove()
                except Exception:
                    pass
                self.grid_cursor = None

    def update_plots(self):
        linestyles = ["-", "--", "-.", ":"]
        linestyle = linestyles[self.plot_count % len(linestyles)]
        nombre_driver = self.sim_names[-1]
        self.plot_count += 1

        if hasattr(self, 'bandpass_system') and self.bandpass_system is not None:
            # Simulación para Bandpass Isobárico
            # Calcular f_max basado en ka ≤ 1 usando los parámetros del driver
            temp_params = {
                'Re': self.user_params['Re'],
                'Qes': self.user_params['Qes'], 
                'Qms': self.user_params['Qms'],
                'Fs': self.user_params['Fs'],
                'Bl': self.user_params['Bl'],
                'Sd': self.user_params['Sd'],
                'Vas': 0.05,  # valor temporal
                'Xmax': 7.5   # valor temporal
            }
            # Calcular Cms desde Vas temporal
            rho0, c = 1.2, 344
            Vas_m3 = temp_params["Vas"] / 1000
            temp_params["Cms"] = Vas_m3 / (rho0 * c**2 * temp_params["Sd"]**2)
            temp_driver = Driver(temp_params)
            f_max_bandpass = temp_driver.f_max_ka(ka_max=1.0)  # Limitar a ka ≤ 1
            
            frequencies = np.logspace(np.log10(5), np.log10(f_max_bandpass), 1000)
            results = self.bandpass_system.simulate(frequencies)
            
            # Usar los resultados del sistema bandpass
            Z_magnitude = results["Zt"]
            Z_phase = results["ZtΦ"]
            SPL_total = results["SPL"]
            SPL_phase = np.zeros_like(SPL_total)  # Bandpass no calcula fase SPL
            displacements_mm = results["DEZ"]  # DEZ está en mm
            velocities = np.ones_like(frequencies)  # Placeholder
            P_real = np.ones_like(frequencies)  # Placeholder
            P_reactiva = np.ones_like(frequencies)  # Placeholder
            P_aparente = np.ones_like(frequencies)  # Placeholder
            P_ac = np.ones_like(frequencies)  # Placeholder
            group_delay_vals = results["groupdelay"]
            
            # Datos para step response (placeholder)
            t_array = np.linspace(0, 0.1, 1000)
            step_t = t_array
            step_x = np.zeros_like(t_array)
            step_v = np.zeros_like(t_array)
            step_a = np.zeros_like(t_array)
            
            efficiency_val = np.ones_like(frequencies)  # Placeholder
            excursion_mm = displacements_mm
            excursion_ratio = np.ones_like(frequencies)
            excursion_peak = np.max(excursion_mm)
            cone_force_array = np.ones_like(frequencies)
            cone_force_peak = 1.0
            xmax_mm = 7.5  # Usar valor por defecto
            f_max = f_max_bandpass  # Usar el límite calculado con ka ≤ 1
            
        else:
            # Simulación normal con Driver
            if self.driver is None:
                return
                
            f_max = self.driver.f_max_ka(ka_max=1.0)  # Limitar a ka ≤ 1
            frequencies = np.logspace(np.log10(5), np.log10(f_max), 1000)
            Z_values = np.array([self.driver.impedance(f) for f in frequencies])
            Z_magnitude = np.abs(Z_values)
            Z_phase = np.angle(Z_values, deg=True)
            SPL_total = np.array([self.driver.spl_total(f) for f in frequencies])
            SPL_phase = np.array([self.driver.spl_phase(f) for f in frequencies])
            displacements = np.array([self.driver.displacement(f) for f in frequencies])
            displacements_mm = displacements * 1000
            velocities = np.array([abs(self.driver.velocity(f)) for f in frequencies])
            P_real = np.array([self.driver.power_real(f) for f in frequencies])
            P_reactiva = np.array([self.driver.power_reactive(f) for f in frequencies])
            P_aparente = np.array([self.driver.power_apparent(f) for f in frequencies])
            P_ac = np.array([self.driver.power_ac(f) for f in frequencies])
            group_delay_vals = -self.driver.group_delay_array(frequencies)
            Fs = abs(self.driver.Fs) if self.driver.Fs != 0 else 1e-6
            T0 = 1 / Fs
            t_array = np.linspace(0, 5 * T0, 1000)
            step_t, step_x, step_v, step_a = self.driver.step_response(t_array)
            efficiency_val = self.driver.efficiency(frequencies)
            excursion_mm, excursion_ratio, excursion_peak, cone_force_array, cone_force_peak = self.driver.excursion(frequencies)
            xmax_mm = self.driver.Xmax

        # --- Grid 3x3 ---
        # Mantén la figura y ejes entre simulaciones
        if self.fig is None or self.axs is None:
            fig = None
            axs = None
        else:
            fig = self.fig
            axs = self.axs

        # Determinar qué driver usar para plot_all
        if hasattr(self, 'bandpass_system') and self.bandpass_system is not None:
            # Para bandpass, crear un objeto pseudo-driver para plot_all
            class PseudoDriver:
                def __init__(self):
                    pass
            plot_driver = PseudoDriver()
        else:
            plot_driver = self.driver

        lines, cursor = plot_all(
            plot_driver, frequencies, Z_magnitude, Z_phase, SPL_total, SPL_phase,
            displacements_mm, velocities, P_real, P_reactiva, P_aparente, P_ac, group_delay_vals, step_t, step_x, step_v,
            step_a, efficiency_val, excursion_mm, excursion_ratio, excursion_peak, cone_force_array, cone_force_peak, xmax_mm, f_max,
            fig=fig, axs=axs, linestyle=linestyle, label=nombre_driver,
            show_legend=self.show_legends,
            enable_cursor=self.enable_grid_cursor,
            grid_cursor=self.grid_cursor
        )
        self.fig = plt.gcf()
        self.axs = np.array(self.fig.axes)
        if self.canvas is not None:
            self.grid_layout.removeWidget(self.canvas)
            self.canvas.setParent(None)
        self.canvas = FigureCanvas(self.fig)
        self.grid_layout.addWidget(self.canvas)

        # --- Pestañas individuales ---
        for i, (tab, layout) in enumerate(self.single_plot_tabs):
            for j in reversed(range(layout.count())):
                widget = layout.itemAt(j).widget()
                if widget is not None:
                    layout.removeWidget(widget)
                    widget.setParent(None)
            fig_single, ax_single = plt.subplots(figsize=(6, 4))
            orig_ax = self.fig.axes[i]  # Usa el índice directo

            # 1. Copia el eje principal
            ax_single.set_xscale(orig_ax.get_xscale())
            ax_single.set_yscale(orig_ax.get_yscale())
            ax_single.set_xlim(orig_ax.get_xlim())
            ax_single.set_ylim(orig_ax.get_ylim())
            ax_single.set_ylabel(orig_ax.get_ylabel())
            ax_single.set_xlabel(orig_ax.get_xlabel())
            ax_single.set_title(orig_ax.get_title())
            ax_single.tick_params(axis='y', labelcolor=orig_ax.yaxis.get_label().get_color())
            # Copia formateadores y localizadores
            ax_single.xaxis.set_major_formatter(orig_ax.xaxis.get_major_formatter())
            ax_single.xaxis.set_major_locator(orig_ax.xaxis.get_major_locator())
            ax_single.yaxis.set_major_formatter(orig_ax.yaxis.get_major_formatter())
            ax_single.yaxis.set_major_locator(orig_ax.yaxis.get_major_locator())
            for line in orig_ax.get_lines():
                ax_single.plot(line.get_xdata(), line.get_ydata(),
                               color=line.get_color(),
                               linestyle=line.get_linestyle(),
                               label=line.get_label(),
                               visible=line.get_visible())
            if len(orig_ax.get_lines()) > 0:
                ax_single.legend(fontsize=8, loc="upper right")
            ax_single.grid(True, which="both")

            # 2. Copia SOLO los twins que son hijos de este subplot (por índice)
            twins = []
            for other_ax in self.fig.axes:
                if other_ax is orig_ax:
                    continue
                if hasattr(other_ax, "spines") and "right" in other_ax.spines:
                    if np.allclose(other_ax.get_position().bounds, orig_ax.get_position().bounds):
                        twins.append(other_ax)
            for idx, orig_twin in enumerate(twins):
                twin = ax_single.twinx()
                orig_pos = orig_twin.spines["right"].get_position()
                if orig_pos != ('outward', 0.0):
                    twin.spines["right"].set_position(orig_pos)
                    twin.set_frame_on(True)
                    twin.patch.set_visible(False)
                twin.set_xscale(orig_twin.get_xscale())
                twin.set_yscale(orig_twin.get_yscale())
                twin.set_xlim(orig_twin.get_xlim())
                twin.set_ylim(orig_twin.get_ylim())
                twin.set_ylabel(orig_twin.get_ylabel())
                twin.tick_params(axis='y', labelcolor=orig_twin.yaxis.get_label().get_color())
                for line in orig_twin.get_lines():
                    twin.plot(line.get_xdata(), line.get_ydata(),
                              color=line.get_color(),
                              linestyle=line.get_linestyle(),
                              label=line.get_label(),
                              visible=line.get_visible())
                if len(orig_twin.get_lines()) > 0:
                    twin.legend(fontsize=8, loc="upper right")
                # --- DESACTIVA la grilla en los twins ---
                twin.grid(False)
                twin.yaxis.grid(False, which='both')
                twin.xaxis.grid(False, which='both')
                for gridline in twin.get_ygridlines() + twin.get_xgridlines():
                    gridline.set_visible(False)

            canvas_single = FigureCanvas(fig_single)
            layout.addWidget(canvas_single)
            fig_single.tight_layout()
            canvas_single.draw()
            # --- Cursor grid en pestañas individuales ---
            if self.enable_grid_cursor:
                import mplcursors
                from visualization.plots import cursor_fmt
                all_lines = []
                for ax in fig_single.axes:
                    all_lines.extend(ax.get_lines())
                cursor = mplcursors.cursor(all_lines, hover=True)
                cursor.connect("add", cursor_fmt)
            # --- Doble clic para maximizar ---
            def on_double_click(event, orig_ax=orig_ax):
                if event.dblclick:
                    from visualization.plots import maximize_subplot
                    maximize_subplot(orig_ax, event)
            canvas_single.mpl_connect("button_press_event", on_double_click)
            plt.close(fig_single)

        # --- Checkboxes ---
        # Solo agrega el nuevo checkbox, no borres los anteriores
        idx = len(self.plot_lines)
        cb = QCheckBox(nombre_driver)
        cb.setChecked(True)
        cb.stateChanged.connect(lambda state, idx=idx: self.toggle_lines(idx))
        self.checkbox_layout.addWidget(cb)
        self.checkboxes.append(cb)
        self.check_vars.append(cb)
        self.plot_lines.append(lines)

    def toggle_lines(self, idx):
        visible = self.check_vars[idx].isChecked()
        for line in self.plot_lines[idx]:
            line.set_visible(visible)
        self.canvas.draw()

# --- MAIN ---
if __name__ == "__main__":
    from main import params, units
    app = QApplication(sys.argv)
    window = AppQt(params, units)
    window.show()
    sys.exit(app.exec_())
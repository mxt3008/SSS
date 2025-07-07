# --------------------------------------------
# plots.py

# --------------------------------------------

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FixedLocator, LogLocator
import matplotlib.ticker as ticker
from matplotlib.ticker import ScalarFormatter
from matplotlib.ticker import FuncFormatter
import matplotlib
import matplotlib.offsetbox

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================
# -------------------------------
# Funciones de visualización para el driver
# -------------------------------

def plot_all(                                                                                                   # Parámetros de entrada
    my_driver, frequencies, Z_magnitude, Z_phase, SPL_total, SPL_phase,                                         # Datos de impedancia y SPL
    displacements_mm, velocities, P_real, P_reactiva, P_aparente, P_ac,                                         # Datos de desplazamientos, velocidades y potencias
    group_delay_vals, step_t, step_x, step_v, step_a, efficiency_val, 
    excursion_mm, excursion_ratio, excursion_peak, cone_force_array, cone_force_peak, xmax_mm,                                     # Datos de retardo de grupo, paso, eficiencia y excursiones
    f_max,                                                                                                      # Frecuencia máxima
    fig=None, axs=None, linestyle="-", label="Simulación", show_legend=True,                                    # Parámetros de visualización
    enable_cursor=False,                                                                                        # Habilitar cursor interactivo
    grid_cursor=None                                                                                            # Cursor de cuadrícula para interactividad
):
    title_fontsize = 8                                                                                          # Tamaño de fuente del título
    label_fontsize = 7                                                                                          # Tamaño de fuente de las etiquetas
    tick_fontsize = 6                                                                                           # Tamaño de fuente de las marcas

    # -------------------------------
    # Configuración de la figura y ejes
    # -------------------------------

    if fig is None or axs is None or not hasattr(plot_all, "_twin_axes"):                                       # Verifica si la figura y los ejes ya están creados
        fig = plt.figure(figsize=(18, 8))                                                                       # Crea una nueva figura si no se proporciona una
        gs = fig.add_gridspec(                                                                                  # Configuración de la cuadrícula de subgráficas
            3, 3,                                                                                               # 3 filas y 3 columnas
            width_ratios=[1, 1, 1],                                                                             # Proporciones de ancho para cada columna
            wspace=0.4,                                                                                         # Espacio horizontal entre subgráficas
            hspace=0.35,                                                                                        # Espacio vertical entre subgráficas
            left=0.05, right=0.95, bottom=0.07, top=0.96                                                       # Márgenes de la figura
        )
        axs = np.array([fig.add_subplot(gs[i, j]) for i in range(3) for j in range(3)])                         # Crea una matriz de subgráficas de 3x3
        axs = axs.flatten()                                                                                     # Aplana la matriz de subgráficas para facilitar el acceso

        plot_all._twin_axes = {}                                                                                # Diccionario para almacenar ejes secundarios
        plot_all._twin_axes[0] = axs[0].twinx()                                                                 # Para Z/fase
        plot_all._twin_axes[1] = axs[1].twinx()                                                                 # Para SPL/fase
    else:
        axs = axs.flatten()                                                                                     # Asegura que axs sea un array plano

    for i in [0, 1, 2, 3, 4, 5, 7, 8]:                                                                          # Limpia los ejes que no se usarán
        axs[i].set_xscale('log', nonpositive='clip')                                                            # Configura el eje x como escala logarítmica

    # -------------------------------
    # Configuración de los ejes secundarios
    # -------------------------------

    twin0 = plot_all._twin_axes[0]                                                                              # Eje secundario para Z y fase
    twin1 = plot_all._twin_axes[1]                                                                              # Eje secundario para SPL y fase
    
    lines = []                                                                                                  # Lista para almacenar las líneas de las gráficas

    #====================================================================================================================================
    # ===============================
    # 1. Gráfica - Impedancia del driver - Magnitud y Fase
    # ===============================

    axs[0].set_title("Impedancia y Fase Eléctrica", fontsize=title_fontsize, fontweight='bold')                 # Título de la gráfica de impedancia
    ax1 = axs[0]                                                                                                # Eje principal para la impedancia
    ln1, = ax1.semilogx(frequencies, Z_magnitude, color="cornflowerblue", linestyle=linestyle, label=f"|Z| [Ω] - {label}") # Magnitud de la impedancia
    ln2, = twin0.semilogx(frequencies, Z_phase, color="darksalmon", linestyle=linestyle, label=f"∠Z [°] - {label}")      # Fase de la impedancia
    ax1.set_ylabel("Impedancia [Ω]", color='cornflowerblue', fontsize=label_fontsize, labelpad=2)                          # Etiqueta del eje y para la impedancia
    twin0.set_ylabel("Fase [°]", color='darksalmon', fontsize=label_fontsize, labelpad=2)                                # Etiqueta del eje y para la fase
    ax1.tick_params(axis='y', labelcolor='cornflowerblue', labelsize=tick_fontsize)                                          # Configuración de las marcas del eje y para la impedancia
    twin0.tick_params(axis='y', labelcolor='darksalmon', labelsize=tick_fontsize, pad=8)                                 # Configuración de las marcas del eje y para la fase
    twin0.yaxis.set_label_coords(1.115, 0.5)                                                                    # Ajusta la posición de la etiqueta del eje y de fase

    lines_imp = [ln1, ln2]                                                                                      # Lista de líneas para la leyenda de impedancia
    labs1 = [l.get_label() for l in lines_imp]                                                                  # Obtiene las etiquetas de las líneas de impedancia
    ax1.legend(lines_imp, labs1, loc='best', fontsize=label_fontsize)                                           # Añade la leyenda a la gráfica de impedancia
    ax1.set_xlabel("Frecuencia [Hz]", fontsize=label_fontsize, labelpad=2)                                      # Etiqueta del eje x
    ax1.tick_params(axis='x', labelsize=tick_fontsize)                                                          # Configuración de las marcas del eje x
    lines.extend([ln1, ln2])                                                                                    # Añade las líneas de impedancia a la lista de líneas

#====================================================================================================================================
    # ===============================
    # 2. Gráfica - SPL - Magnitud y Fase 
    # ===============================

    axs[1].set_title("Respuesta SPL y Fase", fontsize=title_fontsize, fontweight='bold')                            # Título de la gráfica de SPL
    ax_spl = axs[1]                                                                                                 # Eje principal para SPL
    ln3, = ax_spl.semilogx(frequencies, SPL_total, color="cadetblue", linestyle=linestyle, label=f"SPL Total - {label}")    # Magnitud del SPL
    ln4, = twin1.semilogx(frequencies, SPL_phase, color="chocolate", linestyle=linestyle, label=f"Fase SPL [°] - {label}")  # Fase del SPL
    ax_spl.set_ylabel("SPL [dB]", color='cadetblue', fontsize=label_fontsize, labelpad=2)                                   # Etiqueta del eje y para el SPL
    twin1.set_ylabel("Fase [°]", color='chocolate', fontsize=label_fontsize, labelpad=2)                                    # Etiqueta del eje y para la fase del SPL
    ax_spl.tick_params(axis='y', labelcolor='cadetblue', labelsize=tick_fontsize)                                           # Configuración de las marcas del eje y para el SPL
    twin1.tick_params(axis='y', labelcolor='chocolate', labelsize=tick_fontsize, pad=8)                                     # Configuración de las marcas del eje y para la fase del SPL
    twin1.yaxis.set_label_coords(1.115, 0.5)                                                                        # Ajusta la posición de la etiqueta del eje y de fase
    twin1.set_ylim(-180, 180)                                                                                       # Limita el eje y de fase entre -180 y 180 grados

    lns_spl_phase = [ln3, ln4]                                                                                      # Lista de líneas para la leyenda de SPL
    labs_spl_phase = [l.get_label() for l in lns_spl_phase]                                                         # Obtiene las etiquetas de las líneas de fase 
    ax_spl.legend(lns_spl_phase, labs_spl_phase, loc='best', fontsize=label_fontsize)                               # Añade la leyenda a la gráfica e SPL
    ax_spl.set_xlabel("Frecuencia [Hz]", fontsize=label_fontsize, labelpad=2)                                       # Etiqueta del eje x
    ax_spl.tick_params(axis='x', labelsize=tick_fontsize)                                                           # Configuración de las marcas del eje x
    lines.extend([ln3, ln4])                                                                                        # Añade las líneas de SPL a la lista de líneas 

    ax1.grid(True, which="both")                                                                                    # 
    ax_spl.grid(True, which="both")                                                                                 # 

    for twin in [twin0, twin1]:
        twin.grid(False, axis='both')
        twin.xaxis.grid(False, which='both')
        twin.yaxis.grid(False, which='both')
        for gridline in twin.get_xgridlines() + twin.get_ygridlines():
            gridline.set_visible(False)

#====================================================================================================================================
    # ===============================
    # 3. Gráfica - Desplazamiento de la bobina
    # ===============================

    axs[2].set_title("Desplazamiento de la Bobina", fontsize=title_fontsize, fontweight='bold')
    ln_disp, = axs[2].semilogx(frequencies, displacements_mm, color="royalblue", linestyle=linestyle, label=f"Desplazamiento [mm] - {label}")
    axs[2].set_ylabel("Desplazamiento [mm]", color = "royalblue", fontsize=label_fontsize, labelpad=2)
    axs[2].set_xlabel("Frecuencia [Hz]", fontsize=label_fontsize, labelpad=2)
    axs[2].tick_params(axis='both', labelcolor="royalblue", labelsize=tick_fontsize)
    axs[2].legend(fontsize=label_fontsize)
    lines.append(ln_disp)

#====================================================================================================================================
    # ===============================
    # 4. Gráfica - Velocidad del diafragma
    # ===============================

    axs[3].set_title("Velocidad del Cono", fontsize=title_fontsize, fontweight='bold')
    ln6, = axs[3].semilogx(frequencies, velocities, color="darkmagenta", linestyle=linestyle, label=f"Velocidad [m/s] - {label}")
    axs[3].set_ylabel("Velocidad [m/s]", color = "darkmagenta", fontsize=label_fontsize, labelpad=2)
    axs[3].set_xlabel("Frecuencia [Hz]", fontsize=label_fontsize, labelpad=2)
    axs[3].tick_params(axis='both', labelcolor='darkmagenta', labelsize=tick_fontsize)
    axs[3].legend(fontsize=label_fontsize)
    lines.append(ln6)

#====================================================================================================================================
    # ===============================
    # 5. Gráfica - Potencia acústica
    # ===============================

    axs[4].set_title("Potencias Eléctricas y Acústica", fontsize=title_fontsize, fontweight='bold')
    ax5 = axs[4]

    ln7, = ax5.semilogx(frequencies, P_real, color="indianred", linestyle=linestyle, label=f"P. Real [W] - {label}")
    ln8, = ax5.semilogx(frequencies, P_reactiva, color="lightpink", linestyle=linestyle, label=f"P. Reactiva [VAR] - {label}")
    ln9, = ax5.semilogx(frequencies, P_aparente, color="darkorange", linestyle="--", label=f"P. Aparente [VA] - {label}")

    ax5.set_ylabel("Potencias Eléctricas [W/VA]", color='k', fontsize=label_fontsize, labelpad=2)
    ax5.tick_params(axis='y', labelcolor='k', labelsize=tick_fontsize)

    twin5 = ax5.twinx()
    ln10, = twin5.semilogx(frequencies, P_ac, color="seagreen", linestyle=":", label=f"P. Acústica [W] - {label}")
    twin5.set_ylabel("Potencia Acústica [W]", color='seagreen', fontsize=label_fontsize, labelpad=2)
    twin5.tick_params(axis='y', labelcolor='seagreen', labelsize=tick_fontsize)
    twin5.yaxis.set_label_coords(1.12, 0.5)

    ax5.set_xlabel("Frecuencia [Hz]", fontsize=label_fontsize, labelpad=2)
    ax5.tick_params(axis='x', labelsize=tick_fontsize)
    ax5.grid(True, which="both")
    twin5.grid(False)

    lns_power = [ln7, ln8, ln9, ln10]
    labs_power = [l.get_label() for l in lns_power]
    ax5.legend(lns_power, labs_power, fontsize=label_fontsize, loc="lower left")

#====================================================================================================================================
    # ===============================
    # 6. Gráfica - Retardo de grupo
    # ===============================

    axs[5].set_title("Retardo de Grupo", fontsize=title_fontsize, fontweight='bold')
    ln11, = axs[5].semilogx(frequencies, group_delay_vals*1000, color="gold", linestyle=linestyle, label=f"Retardo de Grupo - {label}")
    axs[5].set_ylabel("Tiempo [ms]", color = "goldenrod", fontsize=label_fontsize)
    axs[5].set_xlabel("Frecuencia [Hz]", fontsize=label_fontsize, labelpad=2)
    axs[5].tick_params(axis='both', labelcolor='goldenrod', labelsize=tick_fontsize)
    axs[5].legend(fontsize=label_fontsize)
    lines.append(ln11)

#====================================================================================================================================
    # ===============================
    # 7. Gráfica - Respuesta al escalón
    # ===============================

    axs[6].clear()  # 🔧 Limpia contenido anterior
    axs[6].set_title("Respuesta al Escalón", fontsize=title_fontsize, fontweight='bold')
    axs[6].set_xlabel("Tiempo [ms]", fontsize=label_fontsize)
    axs[6].set_xlim(min(step_t*1000), max(step_t*1000))
    axs[6].set_ylim(auto=True)  # Ajusta automáticamente el límite Y
    axs[6].autoscale(enable=True, axis='y')
    axs[6].grid(True, which="both")
    axs[6].tick_params(axis='both', labelsize=tick_fontsize)

    formatter = FuncFormatter(lambda x, _: f"{x*1000:.0f} ms")
    axs[6].xaxis.set_major_formatter(formatter)
    axs[6].xaxis.set_major_locator(MultipleLocator(0.02))

    axs[6].set_ylabel("Desplazamiento [mm]", fontsize=label_fontsize, color="lightcoral")
    ln_disp, = axs[6].plot(step_t*1000, step_x, color="lightcoral", linestyle=linestyle, label=f"Desplazamiento [mm] - {label}")
    ln_disp.set_gid("Desplazamiento [mm]")
    axs[6].tick_params(axis='y', labelcolor="lightcoral")

    ax_vel = axs[6].twinx()
    ax_vel.set_ylabel("Velocidad [mm/s]", fontsize=label_fontsize, color="darkcyan")
    ln_vel, = ax_vel.plot(step_t*1000, step_v, color="darkcyan", linestyle=linestyle, label=f"Velocidad [mm/s] - {label}")
    ln_vel.set_gid("Velocidad [mm/s]")
    ax_vel.tick_params(axis='y', labelcolor="darkcyan", labelsize=tick_fontsize)

    ax_acc = axs[6].twinx()
    #ax_acc.spines["right"].set_position(("axes", 1.15))  # Mueve este eje más a la derecha
    ax_acc.set_frame_on(True)
    ax_acc.patch.set_visible(False)  # Oculta fondo
    ax_acc.set_ylabel("Aceleración [mm/s²]", fontsize=label_fontsize, color="darkseagreen")
    ln_acc, = ax_acc.plot(step_t*1000, step_a, color="darkseagreen", linestyle=linestyle, label=f"Aceleración [mm/s²] - {label}")
    ln_acc.set_gid("Aceleración [mm/s²]")
    ax_acc.tick_params(axis='y', labelcolor="darkseagreen", labelsize=tick_fontsize)

    lines_step = [ln_disp, ln_vel, ln_acc]
    labels_step = [l.get_label() for l in lines_step]
    axs[6].legend(lines_step, labels_step, fontsize=label_fontsize, loc="upper right")

    lines.extend(lines_step)

#====================================================================================================================================
    # ===============================
    # 8. Gráfica - Eficiencia del driver
    # ===============================

    axs[7].set_title("Eficiencia", fontsize=title_fontsize, fontweight='bold')
    ln13, = axs[7].semilogx(frequencies, efficiency_val, color="firebrick", linestyle=linestyle, label=f"Eficiencia [%] - {label}")        
    axs[7].set_ylabel("Eficiencia [%]", color = "firebrick", fontsize=label_fontsize)
    axs[7].set_xlabel("Frecuencia [Hz]", fontsize=label_fontsize)
    axs[7].set_xscale("log")
    axs[7].tick_params(axis='both', labelcolor='firebrick', labelsize=tick_fontsize)
    axs[7].grid(True, axis='y')
    axs[7].legend(fontsize=label_fontsize, loc="upper right")
    lines.append(ln13)    

#====================================================================================================================================
    # ===============================
    # 9. Gráfica - Excursión, Xmax y Fuerza
    # ===============================

    axs[8].set_title("Excursión pico y Fuerza pico", fontsize=title_fontsize, fontweight='bold')

    # Eje principal: Excursión [mm]
    ax_exc = axs[8]
    ln_exc_mm, = ax_exc.semilogx(frequencies, excursion_mm, color="royalblue", linestyle=linestyle, label=f"Excursión [mm] - {label}")
    ln_xmax, = ax_exc.semilogx(frequencies, np.full_like(frequencies, xmax_mm), color="green", linestyle="--", linewidth=1.5, label=f"Xmax = {xmax_mm:.1f} mm")

    ax_exc.set_ylabel("Excursión [mm]", fontsize=label_fontsize, color="royalblue", labelpad=2)
    ax_exc.tick_params(axis='y', labelcolor="royalblue", labelsize=tick_fontsize)

    # Eje secundario: Fuerza [N]
    ax_force = ax_exc.twinx()
    ln_force, = ax_force.semilogx(frequencies, cone_force_array, color="indianred", linestyle=linestyle, label=f"Fuerza pico [N] - {label}")
    ax_force.set_ylabel("Fuerza [N]", fontsize=label_fontsize, color="indianred", labelpad=2)
    ax_force.tick_params(axis='y', labelcolor="indianred", labelsize=tick_fontsize)
    ax_force.yaxis.set_label_coords(1.12, 0.5)

    # Eje X
    ax_exc.set_xlabel("Frecuencia [Hz]", fontsize=label_fontsize, labelpad=2)
    ax_exc.tick_params(axis='x', labelsize=tick_fontsize)
    ax_exc.grid(True, which="both")

    # Leyenda combinada
    lns_excursion = [ln_exc_mm, ln_xmax, ln_force]
    labels_excursion = [l.get_label() for l in lns_excursion]
    ax_exc.legend(lns_excursion, labels_excursion, fontsize=label_fontsize, loc="upper left")

    # Añadir al conjunto de líneas
    lines.extend(lns_excursion)



#====================================================================================================================================
    # -------------------------------
    # Ajustes finales de los ejes
    # -------------------------------

    custom_ticks = [10, 100, 1000, 10000, 15000, 20000]
    def fmt_ticks(x, pos):
        if x == 0:
            return "0"
        return f"{x/1000:.0f}k" if x >= 1000 else f"{x:.0f}"
    for i, ax in enumerate(axs.flat):
        if i in [0, 1, 2, 3, 4, 5, 7, 8]:  # Subplots que tienen eje X en frecuencia
            ax.set_xscale('log')
            ax.set_xlim([10, (f_max*1.1)])
            ax.xaxis.set_major_locator(FixedLocator(custom_ticks))
            ax.xaxis.set_minor_locator(LogLocator(base=10, subs='auto'))
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(fmt_ticks))
        else:
            ax.set_xscale('linear')  # Subplots de tiempo, como la respuesta al escalón
            ax.set_xlim(auto=True)

        if i not in [0, 1]:
            ax.grid(True, which="both")

    # -------------------------------
    # Limpieza de anotaciones previas y configuración del cursor
    # -------------------------------

    def clean_annotations(fig):
        for ax in fig.axes:
            for child in list(ax.get_children()):
                if isinstance(child, matplotlib.text.Annotation):
                    child.remove()
                if isinstance(child, matplotlib.offsetbox.AnnotationBbox):
                    child.remove()

    cursor = None

    if enable_cursor:
        clean_annotations(fig)
        all_lines = []
        for ax in axs:
            all_lines.extend(ax.get_lines())
            for other in ax.figure.axes:
                if other is not ax and getattr(other, "_sharex", None) is ax:
                    all_lines.extend(other.get_lines())
        import mplcursors
        if grid_cursor is not None:
            try:
                grid_cursor.remove()
            except Exception:
                pass

        cursor = mplcursors.cursor(all_lines, hover=True)

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
    else:
        if grid_cursor is not None:
            try:
                grid_cursor.remove()
            except Exception:
                pass
        clean_annotations(fig)

    # -------------------------------
    # Configuración de las cuadrículas y eliminación de líneas de cuadrícula en los ejes secundarios
    # -------------------------------

    for ax in [twin0, twin1]:
        for gridline in ax.get_ygridlines():
            gridline.set_visible(False)
        ax.grid(False, axis='y')
        ax.yaxis.grid(False, which='both')

    if fig is not None:
        fig.canvas.draw_idle()
        for ax in [twin0, twin1]:
            for gridline in ax.get_ygridlines():
                gridline.set_visible(False)
            ax.grid(False, axis='y')
            ax.yaxis.grid(False, which='both')

    # -------------------------------
    # Configuración de eventos de maximización de subgráficas
    # -------------------------------

    plot_all._subplot_data = {
        0: {  # Impedancia y Fase
            "x": frequencies,
            "y1": Z_magnitude,
            "y2": Z_phase,
            "ylabel1": "Impedancia [Ohm]",
            "ylabel2": "Fase [°]",
            "title": "Impedancia y Fase Eléctrica",
            "label1": "|Z| [Ohm]",
            "label2": "∠Z [°]",
        },
        1: {  # SPL y Fase
            "x": frequencies,
            "y1": SPL_total,
            "y2": SPL_phase,
            "ylabel1": "SPL [dB]",
            "ylabel2": "Fase [°]",
            "title": "Respuesta SPL y Fase",
            "label1": "SPL Total",
            "label2": "Fase SPL [°]",
        },
    }
    return lines, cursor

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

# -------------------------------
# Función para maximizar subgráficas
# -------------------------------

def maximize_subplot(self, event):
    import mplcursors
    ax = event.inaxes
    if ax is None:
        return
    fig = plt.figure(figsize=(8, 6))
    new_ax = fig.add_subplot(111)

    # Copiar líneas del eje principal (plot y axhline)
    # Copiar líneas del eje principal (plot y axhline)
    for line in ax.get_lines():
        x = line.get_xdata()
        y = line.get_ydata()
        label = line.get_label()
        
        # Detectar si es línea horizontal (como Xmax)
        if np.allclose(y, y[0]):
            new_ax.axhline(
                y=y[0],
                color=line.get_color(),
                linestyle=line.get_linestyle(),
                linewidth=line.get_linewidth(),
                label=label
            )
        else:
            new_ax.plot(
                x, y,
                color=line.get_color(),
                linestyle=line.get_linestyle(),
                label=label,
                visible=line.get_visible()
            )



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
    xscale = ax.get_xscale()
    new_ax.set_xscale(xscale)

    if xscale == 'log':
        new_ax.xaxis.set_major_locator(LogLocator(base=10.0, numticks=12))
        new_ax.xaxis.set_minor_locator(LogLocator(base=10.0, subs='auto', numticks=12))
        new_ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{x/1000:.0f}k" if x >= 1000 else f"{x:.0f}"))
    else:
        new_ax.xaxis.set_major_locator(MultipleLocator(100))
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
        if "Escalón" in label or "Escalón" in title or "Step" in label or "Tiempo" in label:
            x_unit = "s"
            y_unit = "mm"
        elif "Eficiencia" in label:
            x_unit = "Hz"
            y_unit = "%"
        elif "∠Z" in label or "Phase" in label or "Fase" in label:
            x_unit = "Hz"
        elif "|Z|" in label:
            y_unit = "Ω"
        elif "SPL" in label:
            y_unit = "dB"
        elif "Desplazamiento" in label:
            y_unit = "mm"
        elif "Velocidad" in label:
            y_unit = "m/s"
        elif "Aceleración" in label:
            y_unit = "m/s²"
        elif "Excursión/Xmax" in label:
            y_unit = "(ratio)"
        elif "Excursión" in label:
            y_unit = "mm"
        elif "Potencia" in label or "P." in label:
            y_unit = "W"
        else:
            y_unit = ""
            sel.annotation.set_text(f"X: {x:.2f} {x_unit}\nY: {y:.2f} {y_unit}")
        sel.annotation.set_text(f"X: {x_label} Hz\nY: {y:.2f} {y_unit}")
    cursor.connect("add", cursor_fmt)
    fig.tight_layout()
    fig.show()
    fig.canvas.draw_idle()
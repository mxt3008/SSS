import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FixedLocator, LogLocator
import matplotlib.ticker as ticker
from matplotlib.ticker import ScalarFormatter
import matplotlib
import matplotlib.offsetbox

def plot_all(
    my_driver, frequencies, Z_magnitude, Z_phase, SPL_total, SPL_phase,
    displacements_mm, velocities, P_real, P_reactiva, P_aparente, P_ac, excursions_mm, 
    group_delay_vals, step_t, step_x, step_v, step_a, efficiency_val, excursion_ratio, f_max,
    fig=None, axs=None, linestyle="-", label="Simulación", show_legend=True,
    enable_cursor=False,
    grid_cursor=None
):
    title_fontsize = 8
    label_fontsize = 7
    tick_fontsize = 6

    # --- Crear figura y ejes la primera vez ---
    if fig is None or axs is None or not hasattr(plot_all, "_twin_axes"):
        fig = plt.figure(figsize=(18, 8))
        gs = fig.add_gridspec(
            3, 3,
            width_ratios=[1, 1, 1],
            wspace=0.3,
            hspace=0.35,
            left=0.08, right=0.985, bottom=0.07, top=0.96
        )
        axs = np.array([fig.add_subplot(gs[i, j]) for i in range(3) for j in range(3)])
        axs = axs.flatten()
        # Crear y guardar los ejes secundarios SOLO la primera vez
        plot_all._twin_axes = {}
        plot_all._twin_axes[0] = axs[0].twinx()  # Para impedancia/fase
        plot_all._twin_axes[1] = axs[1].twinx()  # Para SPL/fase
        #plot_all._twin_axes[4] = axs[4].twinx()  # Para potencias eléctricas/acústica
    else:
        axs = axs.flatten()

    twin0 = plot_all._twin_axes[0]
    twin1 = plot_all._twin_axes[1]

    lines = []

    # 1. Impedancia y Fase Eléctrica
    axs[0].set_title("Impedancia y Fase Eléctrica", fontsize=title_fontsize, fontweight='bold')
    ax1 = axs[0]
    ln1, = ax1.semilogx(frequencies, Z_magnitude, color="b", linestyle=linestyle, label=f"|Z| [Ohm] - {label}")
    ln2, = twin0.semilogx(frequencies, Z_phase, color="r", linestyle=linestyle, label=f"∠Z [°] - {label}")
    ax1.set_ylabel("Impedancia [Ohm]", color='b', fontsize=label_fontsize, labelpad=2)
    twin0.set_ylabel("Fase [°]", color='r', fontsize=label_fontsize, labelpad=2)
    ax1.tick_params(axis='y', labelcolor='b', labelsize=tick_fontsize)
    twin0.tick_params(axis='y', labelcolor='r', labelsize=tick_fontsize, pad=8)
    twin0.yaxis.set_label_coords(1.115, 0.5)

    lns1 = [ln1, ln2]
    labs1 = [l.get_label() for l in lns1]
    if show_legend:
        ax1.legend(lns1, labs1, loc='best', fontsize=label_fontsize)
    ax1.set_xlabel("Frecuencia [Hz]", fontsize=label_fontsize, labelpad=2)
    ax1.tick_params(axis='x', labelsize=tick_fontsize)
    lines.extend([ln1, ln2])

    # 2. SPL y Fase
    axs[1].set_title("Respuesta SPL y Fase", fontsize=title_fontsize, fontweight='bold')
    ax_spl = axs[1]
    ln3, = ax_spl.semilogx(frequencies, SPL_total, color="b", linestyle=linestyle, label=f"SPL Total - {label}")
    ln4, = twin1.semilogx(frequencies, SPL_phase, color="g", linestyle=linestyle, label=f"Fase SPL [°] - {label}")
    ax_spl.set_ylabel("SPL [dB]", color='b', fontsize=label_fontsize, labelpad=2)
    twin1.set_ylabel("Fase [°]", color='g', fontsize=label_fontsize, labelpad=2)
    ax_spl.tick_params(axis='y', labelcolor='b', labelsize=tick_fontsize)
    twin1.tick_params(axis='y', labelcolor='g', labelsize=tick_fontsize, pad=8)
    twin1.yaxis.set_label_coords(1.115, 0.5)
    twin1.set_ylim(-180, 180)

    lns_spl_phase = [ln3, ln4]
    labs_spl_phase = [l.get_label() for l in lns_spl_phase]
    if show_legend:
        ax_spl.legend(lns_spl_phase, labs_spl_phase, loc='best', fontsize=label_fontsize)
    ax_spl.set_xlabel("Frecuencia [Hz]", fontsize=label_fontsize, labelpad=2)
    ax_spl.tick_params(axis='x', labelsize=tick_fontsize)
    lines.extend([ln3, ln4])

    # --- Grid SOLO en el eje principal de las gráficas dobles ---
    ax1.grid(True, which="both")
    ax_spl.grid(True, which="both")
    # --- Fuerza a desactivar el grid del eje secundario (fase) ---
    for twin in [twin0, twin1]:
        twin.grid(False, axis='both')
        twin.xaxis.grid(False, which='both')
        twin.yaxis.grid(False, which='both')
        for gridline in twin.get_xgridlines() + twin.get_ygridlines():
            gridline.set_visible(False)

    # 3. Desplazamiento de la bobina
    axs[2].set_title("Desplazamiento de la Bobina", fontsize=title_fontsize, fontweight='bold')
    ln_disp, = axs[2].semilogx(frequencies, displacements_mm, color="b", linestyle=linestyle, label=f"Desplazamiento [mm] - {label}")
    axs[2].set_ylabel("Desplazamiento [mm]", fontsize=label_fontsize, labelpad=2)
    axs[2].set_xlabel("Frecuencia [Hz]", fontsize=label_fontsize, labelpad=2)
    axs[2].tick_params(axis='both', labelsize=tick_fontsize)
    axs[2].legend(fontsize=label_fontsize)
    lines.append(ln_disp)

    # 4. Velocidad del cono
    axs[3].set_title("Velocidad del Cono", fontsize=title_fontsize, fontweight='bold')
    ln6, = axs[3].semilogx(frequencies, velocities, color="m", linestyle=linestyle, label=f"Velocidad [m/s] - {label}")
    axs[3].set_ylabel("Velocidad [m/s]", fontsize=label_fontsize, labelpad=2)
    axs[3].set_xlabel("Frecuencia [Hz]", fontsize=label_fontsize, labelpad=2)
    axs[3].tick_params(axis='both', labelsize=tick_fontsize)
    axs[3].legend(fontsize=label_fontsize)
    lines.append(ln6)

    # 5. Potencias Eléctricas y Acústica
    axs[4].set_title("Potencias Eléctricas y Acústica", fontsize=title_fontsize, fontweight='bold')
    ax5 = axs[4]

    ln7, = ax5.semilogx(frequencies, P_real, color="b", linestyle=linestyle, label=f"P. Real [W] - {label}")
    ln8, = ax5.semilogx(frequencies, P_reactiva, color="r", linestyle=linestyle, label=f"P. Reactiva [VAR] - {label}")
    ln9, = ax5.semilogx(frequencies, P_aparente, color="orange", linestyle="--", label=f"P. Aparente [VA] - {label}")
    ax5.set_ylabel("Potencias Eléctricas [W/VA]", color='k', fontsize=label_fontsize, labelpad=2)
    ax5.tick_params(axis='y', labelcolor='k', labelsize=tick_fontsize)

    twin5 = ax5.twinx()
    ln10, = twin5.semilogx(frequencies, P_ac, color="g", linestyle=":", label=f"P. Acústica [W] - {label}")
    twin5.set_ylabel("Potencia Acústica [W]", color='g', fontsize=label_fontsize, labelpad=2)
    twin5.tick_params(axis='y', labelcolor='g', labelsize=tick_fontsize)
    twin5.yaxis.set_label_coords(1.12, 0.5)

    ax5.set_xlabel("Frecuencia [Hz]", fontsize=label_fontsize, labelpad=2)
    ax5.tick_params(axis='x', labelsize=tick_fontsize)
    ax5.grid(True, which="both")
    twin5.grid(False)

    lns_power = [ln7, ln8, ln9, ln10]
    labs_power = [l.get_label() for l in lns_power]
    if show_legend:
        ax5.legend(lns_power, labs_power, loc="upper left", fontsize=label_fontsize)

    # 6. Retardo de grupo
    axs[5].set_title("Retardo de Grupo", fontsize=title_fontsize, fontweight='bold')
    ln11, = axs[5].semilogx(frequencies, group_delay_vals, color="m", linestyle=linestyle, label=f"Velocidad [m/s] - {label}")
    axs[5].set_ylabel("Tiempo [s]", fontsize=label_fontsize)
    axs[5].set_xlabel("Frecuencia [Hz]", fontsize=label_fontsize, labelpad=2)
    axs[5].tick_params(axis='both', labelsize=tick_fontsize)
    axs[5].legend(fontsize=label_fontsize)
    lines.append(ln11)

    # 7. Respuesta al escalón
    axs[6].clear()  # 🔧 Limpia contenido anterior
    axs[6].set_title("Respuesta al Escalón", fontsize=title_fontsize, fontweight='bold')
    axs[6].set_xlabel("Tiempo [s]", fontsize=label_fontsize)
    axs[6].set_xlim(min(step_t), max(step_t))
    axs[6].set_ylim(auto=True)  # Ajusta automáticamente el límite Y
    axs[6].autoscale(enable=True, axis='y')
    axs[6].grid(True, which="both")
    axs[6].tick_params(axis='both', labelsize=tick_fontsize)

    axs[6].set_ylabel("Desplazamiento [mm]", fontsize=label_fontsize, color="b")
    ln_disp, = axs[6].plot(step_t, step_x, color="b", linestyle=linestyle, label=f"Desplazamiento [mm] - {label}")
    axs[6].tick_params(axis='y', labelcolor="b")

    ax_vel = axs[6].twinx()
    ax_vel.set_ylabel("Velocidad [mm/s]", fontsize=label_fontsize, color="g")
    ln_vel, = ax_vel.plot(step_t, step_v, color="g", linestyle=linestyle, label=f"Velocidad [mm/s] - {label}")
    ax_vel.tick_params(axis='y', labelcolor="g")

    ax_acc = axs[6].twinx()
    ax_acc.spines["right"].set_position(("axes", 1.15))  # Mueve este eje más a la derecha
    ax_acc.set_frame_on(True)
    ax_acc.patch.set_visible(False)  # Oculta fondo
    ax_acc.set_ylabel("Aceleración [mm/s²]", fontsize=label_fontsize, color="r")
    ln_acc, = ax_acc.plot(step_t, step_a, color="r", linestyle=linestyle, label=f"Aceleración [mm/s²] - {label}")
    ax_acc.tick_params(axis='y', labelcolor="r")

    lines_step = [ln_disp, ln_vel, ln_acc]
    labels_step = [l.get_label() for l in lines_step]
    axs[6].legend(lines_step, labels_step, fontsize=label_fontsize, loc="upper right")

    lines.extend(lines_step)

    # 8. Eficiencia
    axs[7].set_title("Eficiencia", fontsize=title_fontsize, fontweight='bold')
    ln13, = axs[7].semilogx(frequencies, efficiency_val, color="m", linestyle=linestyle, label=f"Eficiencia [%] - {label}")        
    axs[7].set_ylabel("Eficiencia [%]", fontsize=label_fontsize)
    axs[7].set_xlabel("Frecuencia [Hz]", fontsize=label_fontsize)
    axs[7].tick_params(axis='both', labelsize=tick_fontsize)
    axs[7].grid(True, axis='y')
    axs[6].legend(fontsize=label_fontsize)
    lines.append(ln13)    

    # 9. Excursión pico y relación con Xmax
    axs[8].set_title("Excursión pico y Relación con Xmax", fontsize=title_fontsize, fontweight='bold')
    ln14, = axs[8].semilogx(frequencies, excursions_mm, color="b", linestyle=linestyle, label=f"Excursión [mm] - {label}")
    ln15, = axs[8].semilogx(frequencies, excursion_ratio, color="g", linestyle=linestyle, label=f"Excursión/Xmax - {label}")
    hline = axs[8].axhline(1, color="red", linestyle=":", label="Límite Xmax")
    axs[8].legend(fontsize=label_fontsize)
    axs[8].set_xlabel("Frecuencia [Hz]", fontsize=label_fontsize, labelpad=2)
    axs[8].tick_params(axis='both', labelsize=tick_fontsize)
    lines.extend([ln14, ln15])

    # Ajustes de ejes y formato logarítmico
    custom_ticks = [10, 100, 1000, 10000, 15000, 20000]
    def fmt_ticks(x, pos):
        if x == 0:
            return "0"
        return f"{x/1000:.0f}k" if x >= 1000 else f"{x:.0f}"
    for i, ax in enumerate(axs.flat):
        if i in [0, 1, 2, 3, 4, 5, 8]:  # Subplots que tienen eje X en frecuencia
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


    # Limpieza robusta de anotaciones y bbox
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

    # --- SOLUCIÓN FINAL: fuerza a ocultar los gridlines del twin después de todo ---
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
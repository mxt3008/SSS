import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FixedLocator, LogLocator
import matplotlib.ticker as ticker
from matplotlib.ticker import ScalarFormatter
import matplotlib
import matplotlib.offsetbox

def plot_all(
    my_driver, frequencies, Z_magnitude, Z_phase, SPL_total, SPL_phase,
    displacements_mm, velocities, excursions_mm, excursion_ratio, f_max,
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

    # 5. Potencia acústica
    axs[4].set_title("Potencia Acústica", fontsize=title_fontsize, fontweight='bold')
    axs[4].set_xlabel("Frecuencia [Hz]", fontsize=label_fontsize, labelpad=2)
    axs[4].tick_params(axis='both', labelsize=tick_fontsize)

    # 6. Retardo de grupo
    axs[5].set_title("Retardo de Grupo", fontsize=title_fontsize, fontweight='bold')
    axs[5].set_xlabel("Frecuencia [Hz]", fontsize=label_fontsize, labelpad=2)
    axs[5].tick_params(axis='both', labelsize=tick_fontsize)

    # 7. Respuesta al escalón
    axs[6].set_title("Respuesta al Escalón", fontsize=title_fontsize, fontweight='bold')
    axs[6].set_xlabel("Frecuencia [Hz]", fontsize=label_fontsize, labelpad=2)
    axs[6].tick_params(axis='both', labelsize=tick_fontsize)

    # 8. Eficiencia
    axs[7].set_title("Eficiencia", fontsize=title_fontsize, fontweight='bold')
    axs[7].set_xlabel("Frecuencia [Hz]", fontsize=label_fontsize, labelpad=2)
    axs[7].tick_params(axis='both', labelsize=tick_fontsize)

    # 9. Excursión pico y relación con Xmax
    axs[8].set_title("Excursión pico y Relación con Xmax", fontsize=title_fontsize, fontweight='bold')
    ln7, = axs[8].semilogx(frequencies, excursions_mm, color="b", linestyle=linestyle, label=f"Excursión [mm] - {label}")
    ln8, = axs[8].semilogx(frequencies, excursion_ratio, color="g", linestyle=linestyle, label=f"Excursión/Xmax - {label}")
    hline = axs[8].axhline(1, color="red", linestyle=":", label="Límite Xmax")
    axs[8].legend(fontsize=label_fontsize)
    axs[8].set_xlabel("Frecuencia [Hz]", fontsize=label_fontsize, labelpad=2)
    axs[8].tick_params(axis='both', labelsize=tick_fontsize)
    lines.extend([ln7, ln8])

    # Ajustes de ejes y formato logarítmico
    custom_ticks = [10, 100, 1000, 10000, 15000, 20000]
    def fmt_ticks(x, pos):
        if x == 0:
            return "0"
        return f"{x/1000:.0f}k" if x >= 1000 else f"{x:.0f}"
    for i, ax in enumerate(axs.flat):
        ax.set_xscale('log')
        ax.set_xlim([10, (f_max*1.1)])
        ax.xaxis.set_major_locator(FixedLocator(custom_ticks))
        ax.xaxis.set_minor_locator(LogLocator(base=10, subs='auto'))
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(fmt_ticks))
        if i not in [0, 1]:  # Solo activa el grid en los que NO tienen twin
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
        # ...puedes agregar más si quieres otras dobles...
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
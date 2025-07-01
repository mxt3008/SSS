import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FixedLocator, LogLocator
import matplotlib.ticker as ticker
import mplcursors

def plot_all(
    my_driver, frequencies, Z_magnitude, Z_phase, SPL_total, SPL_phase,
    displacements_mm, velocities, excursions_mm, excursion_ratio, f_max,
    fig=None, axs=None
):
    if fig is None or axs is None:
        fig, axs = plt.subplots(3, 3, figsize=(14, 10))
    axs = axs.flatten()
    fig.suptitle("Análisis del Comportamiento de un Parlante en Aire Libre", fontsize=12, fontweight='bold')

    # === 1. Impedancia y Fase ===
    axs[0].set_title("Impedancia y Fase Eléctrica")
    ax1 = axs[0]
    ln1 = ax1.semilogx(frequencies, Z_magnitude, 'b-', label="|Z| [Ohm]")[0]
    ax1.set_ylabel("Impedancia [Ohm]", color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax2 = ax1.twinx()
    ln2 = ax2.semilogx(frequencies, Z_phase, 'r-', label="∠Z [°]")[0]
    ax2.set_ylabel("Fase [°]", color='r')
    ax2.tick_params(axis='y', labelcolor='r')
    lns1 = [ln1, ln2]
    labs1 = [l.get_label() for l in lns1]
    ax1.legend(lns1, labs1, loc='best')
    axs[0].set_xlabel("Frecuencia [Hz]")

    # === 2. SPL y Fase ===
    axs[1].set_title("Respuesta SPL y Fase")
    ax_spl = axs[1]
    ln3 = ax_spl.semilogx(frequencies, SPL_total, label="SPL Total")[0]
    ax_spl.set_ylabel("SPL [dB]", color='b')
    ax_spl.tick_params(axis='y', labelcolor='b')
    ax_spl.yaxis.set_major_locator(MultipleLocator(10))
    ax_phase = ax_spl.twinx()
    ln4 = ax_phase.semilogx(frequencies, SPL_phase, 'g-', label="Fase SPL [°]")[0]
    ax_phase.set_ylabel("Fase [°]", color='g')
    ax_phase.set_ylim(-180, 180)
    ax_phase.tick_params(axis='y', labelcolor='g')
    lns_spl_phase = [ln3, ln4]
    labs_spl_phase = [l.get_label() for l in lns_spl_phase]
    ax_spl.legend(lns_spl_phase, labs_spl_phase, loc='best')
    axs[1].set_xlabel("Frecuencia [Hz]")

    # === 3. Desplazamiento de la bobina ===
    axs[2].set_title("Desplazamiento de la Bobina")
    ln_disp = axs[2].semilogx(frequencies, displacements_mm, label="Desplazamiento [mm]")[0]
    axs[2].set_ylabel("Desplazamiento [mm]")
    axs[2].legend()
    axs[2].set_xlabel("Frecuencia [Hz]")

    # === 4. Velocidad del cono ===
    axs[3].set_title("Velocidad del Cono")
    ln6 = axs[3].semilogx(frequencies, velocities, label="Velocidad [m/s]")[0]
    axs[3].set_ylabel("Velocidad [m/s]")
    axs[3].legend()
    axs[3].set_xlabel("Frecuencia [Hz]")

    # === 5. Potencia acústica ===
    axs[4].set_title("Potencia Acústica")
    axs[4].set_xlabel("Frecuencia [Hz]")

    # === 6. Retardo de grupo ===
    axs[5].set_title("Retardo de Grupo")
    axs[5].set_xlabel("Frecuencia [Hz]")

    # === 7. Respuesta al escalón ===
    axs[6].set_title("Respuesta al Escalón")
    axs[6].set_xlabel("Frecuencia [Hz]")

    # === 8. Eficiencia ===
    axs[7].set_title("Eficiencia")
    axs[7].set_xlabel("Frecuencia [Hz]")

    # === 9. Excursión pico y relación con Xmax ===
    axs[8].set_title("Excursión pico y Relación con Xmax")
    ln7 = axs[8].semilogx(frequencies, excursions_mm, label="Excursión [mm]")[0]
    ln8 = axs[8].semilogx(frequencies, excursion_ratio, '--', label="Excursión/Xmax")[0]
    hline = axs[8].axhline(1, color="red", linestyle=":", label="Límite Xmax")
    axs[8].legend()
    axs[8].set_xlabel("Frecuencia [Hz]")

    # Ajustes de ejes y formato logarítmico
    custom_ticks = [10, 100, 1000, 10000, 15000, 20000]
    def fmt_ticks(x, pos):
        if x == 0:
            return "0"
        return f"{x/1000:.0f}k" if x >= 1000 else f"{x:.0f}"
    for ax in axs.flat:
        ax.set_xscale('log')
        ax.set_xlim([10, (f_max*1.1)])
        ax.xaxis.set_major_locator(FixedLocator(custom_ticks))
        ax.xaxis.set_minor_locator(LogLocator(base=10, subs='auto'))
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(fmt_ticks))
        ax.grid(True, which="both")

    # Cursores interactivos
    extra_axes = [ax2, ax_phase]
    interactive_axes = []
    for ax in axs:
        v = ax.axvline(x=0, color='gray', linestyle='--', lw=0.6, zorder=10)
        h = ax.axhline(y=0, color='gray', linestyle='--', lw=0.6, zorder=10)
        v.set_visible(False)
        h.set_visible(False)
        interactive_axes.append((ax, h, v))
    for twin_ax in extra_axes:
        v = twin_ax.axvline(x=0, color='gray', linestyle='--', lw=0.6, zorder=10)
        h = twin_ax.axhline(y=0, color='gray', linestyle='--', lw=0.6, zorder=10)
        v.set_visible(False)
        h.set_visible(False)
        interactive_axes.append((twin_ax, h, v))

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

    all_lines = [ln1, ln2, ln3, ln4, ln_disp, ln6, ln7, ln8, hline]
    cursor = mplcursors.cursor(all_lines, hover=True)
    cursor.connect("add", cursor_fmt)

    plt.tight_layout()

    # Cursores dinámicos con líneas cruzadas
    def on_mouse_move(event):
        if not event.inaxes:
            return
        ax = event.inaxes
        closest_axis = None
        closest_line = None
        closest_y = None
        min_dist = float('inf')
        for axis, hline, vline in interactive_axes:
            if axis != ax:
                continue
            for line in axis.get_lines():
                if not line.get_visible():
                    continue
                xdata = line.get_xdata()
                ydata = line.get_ydata()
                if len(xdata) == 0:
                    continue
                try:
                    x = event.xdata
                    if x is None:
                        continue
                    y_interp = np.interp(x, xdata, ydata)
                    y_disp = axis.transData.transform((x, y_interp))[1]
                    dist = abs(event.y - y_disp)
                    if dist < min_dist:
                        min_dist = dist
                        closest_axis = axis
                        closest_line = line
                        closest_y = y_interp
                except:
                    continue
        for _, hline, vline in interactive_axes:
            hline.set_visible(False)
            vline.set_visible(False)
        if closest_axis is not None and closest_y is not None:
            for axis, hline, vline in interactive_axes:
                if axis == closest_axis:
                    x = event.xdata
                    vline.set_xdata([x, x])
                    hline.set_ydata([closest_y, closest_y])
                    vline.set_visible(True)
                    hline.set_visible(True)
            fig.canvas.draw_idle()
    fig.canvas.mpl_connect("motion_notify_event", on_mouse_move)

    # Doble clic para maximizar/restaurar subplots
    twinx_map = {
        axs[0]: ax2,
        axs[1]: ax_phase,
    }
    all_twinx = set(twinx_map.values())
    maximized_ax = None
    original_positions = {}

    def on_double_click(event):
        nonlocal maximized_ax, original_positions
        if event.dblclick and event.inaxes in list(axs) + list(all_twinx):
            ax = event.inaxes
            main_ax = None
            for k, v in twinx_map.items():
                if ax == k or ax == v:
                    main_ax = k
                    break
            if main_ax is None:
                main_ax = ax
            twin_ax = twinx_map.get(main_ax, None)
            if maximized_ax is None:
                original_positions.clear()
                for a in axs:
                    original_positions[a] = a.get_position().frozen()
                    a.set_visible(False)
                for t in all_twinx:
                    original_positions[t] = t.get_position().frozen()
                    t.set_visible(False)
                main_ax.set_visible(True)
                main_ax.set_position([0.07, 0.07, 0.86, 0.86])
                if twin_ax:
                    twin_ax.set_visible(True)
                    twin_ax.set_position([0.07, 0.07, 0.86, 0.86])
                maximized_ax = main_ax
                fig.canvas.draw_idle()
            else:
                for a in axs:
                    a.set_position(original_positions[a])
                    a.set_visible(True)
                for t in all_twinx:
                    t.set_position(original_positions[t])
                    t.set_visible(True)
                maximized_ax = None
                fig.canvas.draw_idle()
    fig.canvas.mpl_connect("button_press_event", on_double_click)

    return fig, axs
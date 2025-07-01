import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FixedLocator, LogLocator
import matplotlib.ticker as ticker
import mplcursors

def plot_all(
    my_driver, frequencies, Z_magnitude, Z_phase, SPL_total, SPL_phase,
    displacements_mm, velocities, excursions_mm, excursion_ratio, f_max,
    fig=None, axs=None, linestyle="-"
):
    if fig is None or axs is None:
        fig, axs = plt.subplots(3, 3, figsize=(14, 10))
    axs = axs.flatten()
    fig.suptitle("Análisis del Comportamiento de un Parlante en Aire Libre", fontsize=12, fontweight='bold')

    lines = []

    # === 1. Impedancia y Fase ===
    axs[0].set_title("Impedancia y Fase Eléctrica")
    ax1 = axs[0]
    ln1, = ax1.semilogx(frequencies, Z_magnitude, color="b", linestyle=linestyle, label="|Z| [Ohm]")
    ax1.set_ylabel("Impedancia [Ohm]", color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax2 = ax1.twinx()
    ln2, = ax2.semilogx(frequencies, Z_phase, color="r", linestyle=linestyle, label="∠Z [°]")
    ax2.set_ylabel("Fase [°]", color='r')
    ax2.tick_params(axis='y', labelcolor='r')
    lns1 = [ln1, ln2]
    labs1 = [l.get_label() for l in lns1]
    ax1.legend(lns1, labs1, loc='best')
    axs[0].set_xlabel("Frecuencia [Hz]")
    lines.extend([ln1, ln2])

    # === 2. SPL y Fase ===
    axs[1].set_title("Respuesta SPL y Fase")
    ax_spl = axs[1]
    ln3, = ax_spl.semilogx(frequencies, SPL_total, color="b", linestyle=linestyle, label="SPL Total")
    ax_spl.set_ylabel("SPL [dB]", color='b')
    ax_spl.tick_params(axis='y', labelcolor='b')
    ax_spl.yaxis.set_major_locator(MultipleLocator(10))
    ax_phase = ax_spl.twinx()
    ln4, = ax_phase.semilogx(frequencies, SPL_phase, color="g", linestyle=linestyle, label="Fase SPL [°]")
    ax_phase.set_ylabel("Fase [°]", color='g')
    ax_phase.set_ylim(-180, 180)
    ax_phase.tick_params(axis='y', labelcolor='g')
    lns_spl_phase = [ln3, ln4]
    labs_spl_phase = [l.get_label() for l in lns_spl_phase]
    ax_spl.legend(lns_spl_phase, labs_spl_phase, loc='best')
    axs[1].set_xlabel("Frecuencia [Hz]")
    lines.extend([ln3, ln4])

    # === 3. Desplazamiento de la bobina ===
    axs[2].set_title("Desplazamiento de la Bobina")
    ln_disp, = axs[2].semilogx(frequencies, displacements_mm, color="b", linestyle=linestyle, label="Desplazamiento [mm]")
    axs[2].set_ylabel("Desplazamiento [mm]")
    axs[2].legend()
    axs[2].set_xlabel("Frecuencia [Hz]")
    lines.append(ln_disp)

    # === 4. Velocidad del cono ===
    axs[3].set_title("Velocidad del Cono")
    ln6, = axs[3].semilogx(frequencies, velocities, color="m", linestyle=linestyle, label="Velocidad [m/s]")
    axs[3].set_ylabel("Velocidad [m/s]")
    axs[3].legend()
    axs[3].set_xlabel("Frecuencia [Hz]")
    lines.append(ln6)

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
    ln7, = axs[8].semilogx(frequencies, excursions_mm, color="b", linestyle=linestyle, label="Excursión [mm]")
    ln8, = axs[8].semilogx(frequencies, excursion_ratio, color="g", linestyle=linestyle, label="Excursión/Xmax")
    hline = axs[8].axhline(1, color="red", linestyle=":", label="Límite Xmax")
    axs[8].legend()
    axs[8].set_xlabel("Frecuencia [Hz]")
    lines.extend([ln7, ln8])

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
    all_lines = [ln1, ln2, ln3, ln4, ln_disp, ln6, ln7, ln8, hline]
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

    plt.tight_layout()
    return lines
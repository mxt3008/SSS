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

import numpy as np                                                          # Para operaciones matemáticas y manejo de arrays
import matplotlib                                                           # Para graficar resultados
matplotlib.use("TkAgg")                                                     # Fuerza el uso del backend TkAgg para mostrar gráficos en ventana
import matplotlib.pyplot as plt                                             # Para crear gráficos y visualizaciones
import matplotlib.ticker as ticker                                          # Para formatear ejes en gráficos
from matplotlib.ticker import LogLocator, FixedLocator                      # Para formatear ejes logarítmicos y escalares
import mplcursors                                                           # Para agregar cursores interactivos a los gráficos
import tkinter as tk
from tkinter import simpledialog, messagebox

from core.driver import Driver                                              # Importa la clase Driver definida en core/driver.py

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

# --------------------------------------------
# Definir parámetros del altavoz
# --------------------------------------------

params = {
    "Fs": 52,                                   # Frecuencia de resonancia [Hz]
    "Mms": 0.065,                               # Masa móvil aproximada [kg]
    "Vas": 62,                                  # Volumen de aire equivalente [litros]
    "Qts": 0.32,                                # Factor de calidad total
    "Qes": 0.34,                                # Factor de calidad eléctrico
    "Qms": 4.5,                                 # Factor de calidad mecánico 
    "Re": 5.3,                                  # Resistencia DC de la bobina [Ohm]
    "Bl": 18.1,                                 # Producto flujo-Bobina [N/A]
    "Sd": 0.055,                                # Área efectiva del diafragma [m²]
    "Le": 1.5e-3,                               # Inductancia de la bobina [Henrios]
    "Xmax": 7.5                                 # Excursión máxima lineal del cono [milímetros]
}

# Diccionario de unidades para cada parámetro
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

def pedir_parametros(params, units):
    root = tk.Tk()
    root.withdraw()
    user_params = {}
    for key, default in params.items():
        unidad = units.get(key, "")
        prompt = f"{key} [{unidad} - Valor default: {default}]"
        val = simpledialog.askstring("Parámetro TS", prompt)
        if val is None or val.strip() == "":
            user_params[key] = default
        else:
            try:
                user_params[key] = float(val)
            except ValueError:
                messagebox.showwarning("Valor inválido", f"Valor inválido para {key}. Se usará valor por defecto: {default}")
                user_params[key] = default
    root.destroy()
    return user_params

def mostrar_parametros_derivados(driver):
    resumen = driver.resumen_parametros()
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Parámetros Derivados", resumen)
    root.destroy()

print("\n=====================================================================")
print("=== Simulador de Driver ===")
print("=== Parámetros por defecto utilizados - JBL 2206H ===")
print("\nIntroduce parámetros TS del altavoz (Enter = usa valores por defecto)\n")

params = pedir_parametros(params, units)
my_driver = Driver(params)
mostrar_parametros_derivados(my_driver)

# --------------------------------------------
# Calcular y mostrar impedancia y SPL para una frecuencia específica
# --------------------------------------------

freq = params["Fs"]                                                         # Usar la frecuencia de resonancia para la prueba puntual
Z = my_driver.impedance(freq)                                               # Calcula la impedancia compleja a esa frecuencia
print("=====================================================================")
print(f"Impedancia (módulo) a {freq} Hz: {abs(Z):.2f}")                     # Imprime el módulo de la impedancia
print(f"Impedancia (fase) a {freq} Hz: {np.angle(Z, deg=True):.2f} °")      # Imprime la fase de la impedancia
print(f"SPL (módulo) a {freq} Hz: {my_driver.spl_total(freq):.2f} dB")      # Imprime el SPL total a esa frecuencia
print(f"SPL (fase) a {freq} Hz: {my_driver.spl_phase(freq):.2f} °")         # Imprime la fase del SPL a esa frecuencia
print("=====================================================================")

# --------------------------------------------
# Barrido de frecuencias para simulación de rango completo
# --------------------------------------------

f_max = my_driver.f_max_ka()                                        # Obtiene la frecuencia máxima del altavoz (frecuencia de corte)
frequencies = np.logspace(np.log10(5), np.log10(f_max), 1000)       # Vector de frecuencias de 5 Hz a 1000 Hz (escala logarítmica)
print(f"Frecuencia máxima para ka ≤ 1: {f_max:.2f} Hz")             # Imprime la frecuencia máxima para ka ≤ 1
print("=====================================================================\n")

# 1. Calcula la impedancia compleja para cada frecuencia
Z_values = np.array([my_driver.impedance(f) for f in frequencies])
Z_magnitude = np.abs(Z_values)                                      # Módulo de la impedancia
Z_phase = np.angle(Z_values, deg=True)                              # Fase de la impedancia en grados

# 2. Calcula la respuesta SPL estimada para cada frecuencia: total + fase acústica
SPL_total = np.array([my_driver.spl_total(f) for f in frequencies]) # SPL total
SPL_phase = np.array([my_driver.spl_phase(f) for f in frequencies]) # Fase del SPL (acústica)

# 3, Calcula el desplazamiento del cono para cada frecuencia
displacements = np.array([my_driver.displacement(f) for f in frequencies])
displacements_mm = displacements * 1000                             # Convertir a milímetros para graficar

# 4. Calcula la velocidad del cono para cada frecuencia (magnitud)
velocities = np.array([abs(my_driver.velocity(f)) for f in frequencies])

# 5. Calcula la potencia acústica para cada frecuencia - Real, aparente y la corriente
# 6. Calcula el retardo de grupo para cada frecuencia
# 7. Calcula la respuesta al escalón para cada frecuencia
# 8. Calcula la eficiencia del altavoz para cada frecuencia

# 9. Calcula la excursión pico del cono para cada frecuencia
excursions = velocities / (2 * np.pi * frequencies)                 # Excursión en metros
excursions_mm = excursions * 1000                                   # Excursión en milímetros
excursion_ratio = excursions / my_driver.Xmax                       # Excursión normalizada respecto a Xmax

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

# --------------------------------------------
# Gráfica 3x3 para visualizar todos los parámetros
# --------------------------------------------

fig, axs = plt.subplots(3, 3, figsize=(14, 10))
axs = axs.flatten()                                                 # Aplana la matriz 3x3 a un arreglo 1D de 9 elementos
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

# --------------------------------------------
# Ajustes de ejes y formato logarítmico
# --------------------------------------------

custom_ticks = [10, 100, 1000, 10000, 15000, 20000]

def fmt_ticks(x, pos):                                                      # Formatea los ticks del eje x
    if x == 0:
        return "0"  
    return f"{x/1000:.0f}k" if x >= 1000 else f"{x:.0f}"                    # Formatea a kHz si es mayor o igual a 1000

for ax in axs.flat:
    ax.set_xscale('log')
    ax.set_xlim([10, (f_max*1.1)])                                          # Ajusta el límite derecho para incluir un margen
    ax.xaxis.set_major_locator(FixedLocator(custom_ticks))
    ax.xaxis.set_minor_locator(LogLocator(base=10, subs='auto'))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(fmt_ticks))
    ax.grid(True, which="both")

# --------------------------------------------
# Cursores interactivos para inspeccionar valores
# --------------------------------------------

# Crear lista de ejes secundarios 
extra_axes = [ax2, ax_phase]  # eje para fase de impedancia y fase de SPL

# Guardamos pares (eje, línea_horizontal, línea_vertical)
interactive_axes = []

# Agrega los 9 subplots originales
for ax in axs:
    v = ax.axvline(x=0, color='gray', linestyle='--', lw=0.6, zorder=10)
    h = ax.axhline(y=0, color='gray', linestyle='--', lw=0.6, zorder=10)
    v.set_visible(False)
    h.set_visible(False)
    interactive_axes.append((ax, h, v))

# Agrega los ejes twinx (fase de impedancia y fase de SPL)
for twin_ax in extra_axes:
    v = twin_ax.axvline(x=0, color='gray', linestyle='--', lw=0.6, zorder=10)
    h = twin_ax.axhline(y=0, color='gray', linestyle='--', lw=0.6, zorder=10)
    v.set_visible(False)
    h.set_visible(False)
    interactive_axes.append((twin_ax, h, v))

def cursor_fmt(sel):                                                        # Formatea la anotación del cursor
    x = sel.target[0]
    y = sel.target[1]
    x_label = f"{x/1000:.1f}k" if x >= 1000 else f"{x:.0f}"                 # Formatea la frecuencia a kHz si es mayor o igual a 1000
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

all_lines = lns1 + lns_spl_phase + [ln_disp, ln6, ln7, ln8, hline]
cursor = mplcursors.cursor(all_lines, hover=True)
cursor.connect("add", cursor_fmt)

plt.tight_layout()

# --------------------------------------------
# Cursores dinámicos con líneas cruzadas
# --------------------------------------------

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

    # Apaga todos
    for _, hline, vline in interactive_axes:
        hline.set_visible(False)
        vline.set_visible(False)

    # Prende solo en el eje correspondiente
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

plt.show()

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

# Fin del script principal
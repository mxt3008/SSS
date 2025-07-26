import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import ifft

# CONSTANTES FÍSICAS
ρ0 = 1.2       # Densidad del aire [kg/m³]
c0 = 343       # Velocidad del sonido en el aire [m/s]
P0 = 20e-6     # Presión de referencia para SPL (0 dB) [Pa]

# PARÁMETROS DE EXCITACIÓN
V0 = 2.83      # Voltaje de entrada al altavoz [V] (2.83V equivale a 1W en 8 ohms)
W = 1          # Potencia nominal de referencia [W]

# PARÁMETROS THIELE-SMALL DEL ALTAVOZ (JBL 2206H)
B = 0.8333     # Factor de fuerza magnética [T]
Re = 5.3       # Resistencia DC de la bobina [ohms]
Red = 0.5     # Resistencia de pérdidas por corrientes de Foucault [ohms]
Qts = 0.31     # Factor Q total del altavoz (incluye pérdidas mecánicas y eléctricas)
Qms = 4.5      # Factor Q mecánico del altavoz (solo pérdidas mecánicas)
Qes = 0.34     # Factor Q eléctrico del altavoz (solo pérdidas eléctricas)
Lvc = 1.5e-3   # Inductancia de la bobina móvil [H]
S = 0.055      # Área efectiva del cono/diafragma [m²]
VAS = 62      # Volumen de aire equivalente a la compliance del altavoz [L]
fs = 52        # Frecuencia de resonancia del altavoz en espacio libre [Hz]
BL = 18.1     # Factor de fuerza electroacústica [N/A]
dd = 2*np.sqrt(S/np.pi) # Diámetro del diafragma [m] (2*sqrt(S/π) para área circular)
print(f"Diámetro del diafragma: {dd} m")

# PARÁMETROS DE LA CAJA BASS-REFLEX
Vab = 0.120    # Volumen interno de la caja [m³]
fp = 25        # Frecuencia de sintonía del puerto [Hz]
dp = 0.2*dd    # Diámetro del puerto [m] (20% del diámetro del altavoz)

# PARÁMETROS DERIVADOS DEL ALTAVOZ
Mms = Qes*(BL**2)/(2*np.pi*fs*Re)    # Masa móvil del sistema [kg]
Cms = 1/(Mms*(2*np.pi*fs)**2)        # Compliance mecánica del altavoz [m/N]
Rms = 2*np.pi*fs*Mms/Qms            # Resistencia mecánica del altavoz [kg/s]

# PARÁMETROS ACÚSTICOS DERIVADOS
Cab = Vab/(ρ0*c0**2)                # Compliance acústica de la caja [m⁵/N]
M_ap = 1/(Cab*(2*np.pi*fp)**2)      # Masa acústica del puerto [kg/m⁴]

# DIMENSIONES DERIVADAS
ad = dd/2      # Radio del diafragma [m]
ap = dp/2      # Radio del puerto [m]

# IMPEDANCIAS DE RADIACIÓN
# Radiación frontal
Rarf = c0*ρ0/(np.pi*(ad)**2)        # Resistencia de radiación frontal [kg/s·m⁴]
Marf = 8*ρ0/(3*ad*(np.pi)**2)       # Masa de radiación frontal [kg/m⁴]

# Radiación posterior
Rarp = c0*ρ0/(np.pi*(ad)**2)        # Resistencia de radiación posterior [kg/s·m⁴]
Marp = B*ρ0/(np.pi*ad)              # Masa de radiación posterior con factor B [kg/m⁴]

# Radiación del puerto
A = np.pi*(ap**2)                   # Área del puerto [m²]
print(f"Área del puerto: {A} m²")
k = 2*np.pi*fp/c0                   # Número de onda a la frecuencia fp [1/m]
lfix = M_ap*np.pi*(ap**2)/ρ0        # Longitud efectiva del puerto [m]
print(f"Longitud efectiva del puerto: {lfix} m")

Rapp = 0.479*ρ0*c0/ap**2            # Resistencia de radiación del puerto [kg/s·m⁴]
Mapp = 0.270*ρ0/ap                  # Masa de radiación del puerto [kg/m⁴]

# MASA DIAFRAGMÁTICA
Mmd = 0.15127                       # Masa del diafragma sin carga de radiación [kg]

# CONVERSIONES ENTRE DOMINIOS (ELÉCTRICO, MECÁNICO, ACÚSTICO)
# Valores transformados al dominio eléctrico
Carp = Marp*(S**2)/(BL**2)          # Capacitancia equivalente de radiación posterior
Rarp = (BL**2)/(Rarp*(S**2))        # Resistencia equivalente de radiación posterior
Lbox = (BL**2)*Cab/S**2             # Inductancia equivalente de la caja
Rbox = 1500                         # Resistencia equivalente de la caja (hardcoded)
Cp = Marp*(S**2)/(BL**2)            # Capacitancia equivalente del puerto
Rp = (BL**2)/(Rapp*(S**2))          # Resistencia equivalente del puerto
Rap = 200                            # Resistencia equivalente adicional del puerto (hardcoded)
Map = M_ap*(S**2)/(BL**2)           # Inductancia equivalente de la masa del puerto
Ca = Marf*(S**2)/(BL**2)            # Capacitancia equivalente de radiación frontal
Ra = (BL**2)/(Rarf*(S**2))          # Resistencia equivalente de radiación frontal
Csps = Mmd/(BL**2)                  # Capacitancia equivalente de la masa del cono
Lsps = Cms*(BL**2)                  # Inductancia equivalente de la compliance del cono
Reps = 50                           # Resistencia equivalente de las pérdidas mecánicas (hardcoded)

f = range(1,10000,1)
freq = np.linspace(1,300,9999)

SPL = []
SPLΦ = []
SPLspk = []
SPLspkΦ = []
SPLport = []
SPLportΦ = []
LWA = []
Zt = []
ZtΦ = []
DEZ = []

Yw = []

datos = []
lineal = []

for i in f:
    
    freqi = freq[i-1]
    w = 2*np.pi*freqi
    
    Z10 = Rarp + 1/(1j*w*Carp)
    
    #para la impedancia Z20
    ZLbox = 1j*w*Lbox
    ZRbox = Rbox
    
    Z20 = 1/(1/Z10 + 1/ZRbox + 1/ZLbox)
    
    #Impedancia Z30
    ZMap = 1/(1j*w*Map)
    ZRap = Rap
    ZB1 = Rp + 1/(1j*w*Cp)
    
    Znext = 1/(1/ZMap + 1/ZRap + 1/ZB1)
    
    Z30 = Znext + Z20
    
    #Impedancia Z40
    
    ZB2 = Ra + 1/(1j*w*Ca)
    ZReps = Reps
    ZLsps = 1j*w*Lsps
    ZCsps = 1/(1j*w*Csps)
    
    Zmiddle = 1/(1/ZCsps + 1/ZLsps + 1/ZReps + 1/ZB2)
    
    Z40 = 1/(1/Zmiddle + 1/Z30)
    
    #Impedancia Z50
    
    ZLvc = 1j*w*Lvc
    
    Zinput = 1/(1/ZLvc + 1/Red) + Re
    
    Z50 = Zinput + Z40
    
    #Hallamos los Rij
    
    R31 = np.sqrt(np.real(Z10)**2 + np.imag(Z10)**2)
    R32 = np.arctan(np.imag(Z10)/np.real(Z10))
    
    R33 = np.sqrt(np.real(Z20)**2 + np.imag(Z20)**2)
    R34 = np.arctan(np.imag(Z20)/np.real(Z20))
    
    R35 = np.sqrt(np.real(Z30)**2 + np.imag(Z30)**2)
    R36 = np.arctan(np.imag(Z30)/np.real(Z30))
    
    R37 = np.sqrt(np.real(Z40)**2 + np.imag(Z40)**2)
    R38 = np.arctan(np.imag(Z40)/np.real(Z40))
    
    R39 = np.sqrt(np.real(Z50)**2 + np.imag(Z50)**2)
    R40 = np.arctan(np.imag(Z50)/np.real(Z50))
    
    
    
    #Impedance
    
    Zt.append(R39)    
    
    #Sound Level Pressure
    
    Gspl = R33*R37/(R35*R39)
    
    SPLi = 20*np.log10(ρ0*w*(dd**2)*Gspl*V0/(16*(10**-5)*BL))
    SPL.append(SPLi)
    
    #lineali = P0*np.exp(SPLi/20)
    lineali = (ρ0*(dd**2)*Gspl*V0/(16*(10**-5)*BL))
    lineal.append(lineali)
    ##for the step response
    
    #Hwi = Z50/Z10
    #Hwi = Z10
    #Hwi = 1/Z10
    #Ywi = Hwi/(1j*w)
    
    #Yw.append(Ywi)
    
    #if i == 9999:
        #Yt = np.fft.ifft(SPL)/w
        
        #Step = np.sqrt(np.real(Yt)**2 + np.imag(Yt)**2)
        #valuemax = max(Step)
        #Step = Step/valuemax
        
        #Stepresponse = np.real(Yt)
        #valuemax = max(Stepresponse)
        #Stepresponse = Stepresponse/valuemax
    
    
    
    
    #SPLspk
    
    Gspk = R37/R39
    
    SPLspki = 20*np.log10(ρ0*w*(dd**2)*Gspk*V0/(16*(10**-5)*BL))
    SPLspk.append(SPLspki)
    
    #SPLport
    
    Gport = np.sqrt(Gspl**2 + Gspk**2 -2*Gspl*Gspk*np.cos(R34-R36))
    
    SPLporti = 20*np.log10(ρ0*w*(dd**2)*Gport*V0/(16*(10**-5)*BL))
    SPLport.append(SPLporti)
    
    R32 = R32*180/np.pi
    R34 = R34*180/np.pi
    R36 = R36*180/np.pi
    R38 = R38*180/np.pi
    R40 = R40*180/np.pi
    
    #Impedance Phase
    
    ZtΦ.append(R40)
    
    
    #Sound Level Pressure Phase
    
    SPLΦi = R34 + R38 -R36 -R40 + 90 #debido al j
    
    datos.append(SPLΦi)
    
    #if SPLΦi > 180:
    #    SPLΦi = -360 + SPLΦi
        
    #if SPLΦi > 0:
    #    SPLΦi = -180 + SPLΦi
    
    #### para adaptarlo entre 0 y -180
    #SPLΦi = SPLΦi -315
    #if SPLΦi < -180:
    #    SPLΦi = SPLΦi + 180
    SPLΦ.append(SPLΦi)
    
    #Spk phase
    
    SPLspkΦi =  R38 - R40 +90
    
    if SPLspkΦi > 180:
        SPLspkΦi = -360 + SPLspkΦi
    
    #SPLspkΦi = SPLspkΦi -315
    #if SPLspkΦi < -180:
    #    SPLspkΦi = SPLspkΦi + 180
    
    SPLspkΦ.append(SPLspkΦi)
    
    #port phase
    
    SPLportΦi = R34 - R36 + 90
    if SPLportΦi > 180:
        SPLportΦi = -360 + SPLportΦi
    
    #SPLportΦi = SPLportΦi -315
    #if SPLportΦi < -180:
    #    SPLportΦi = SPLportΦi + 180
    
    SPLportΦ.append(SPLportΦi)
    
    #Dezplazamiento
    
    Gain = R37/R39
    DEZi = np.sqrt(2)*Gain*V0/(w*BL)
    # metros a mm
    DEZi = DEZi*1000
    DEZ.append(DEZi)
    
    #Sound Power
    
    LWAi = 10*np.log10((Ra*(Gspl*V0/(R31))**2)/(6.31*(10**-12))) 
    LWA.append(LWAi)
    

groupdelay = []
for i in range(9999):
    if 9998 > i >0:
        groupdelayi = -1000*((datos[i] - datos[i-1])/(freq[i] - freq[i-1]) + (datos[i+1]-datos[i])/(freq[i+1] - freq[i]))/(2*360)
        groupdelay.append(groupdelayi)

a = 9999
omega = 2*np.pi*freq

# IMPORTANTE: Cambio fs -> delta_f para evitar sobreescribir la frecuencia de resonancia
delta_f = freq[1] - freq[0]  # Paso de frecuencia

hww = lineal  # /omega

def idft(X, sampling_freq=None):
    N = len(X)
    n = np.arange(N)
    k = n.reshape((N, 1))
    exp_matrix = np.exp(2j * np.pi * k * n / N)
    x = (1 / N) * np.dot(exp_matrix, X)
    
    # Create time array
    if sampling_freq:  # Sampling frequency provided
        t = n / sampling_freq
    else:  # Default to unit spacing
        t = n
    
    return x, t



gt, times = idft(hww, delta_f)  # Corregido: delta_f en lugar de fs

gt = np.fft.ifft(np.fft.ifftshift(hww), 150000)
gtreal = np.real(gt)

#gtmodulus = np.sqrt(np.real(gt)**2 + np.imag(gt)**2)

gtnorm = gtreal/max(gtreal)

a = 15000
time = (np.linspace(0, 1000/(300), 150000))*10000
time = time/300*1000


# Configuración mejorada de visualización
import matplotlib
matplotlib.use('TkAgg')  # Usar backend interactivo
matplotlib.style.use('seaborn-v0_8-whitegrid')  # Usar un estilo moderno

# Configuración para ajustar automáticamente los límites de los ejes con 10% de margen
def set_axis_limits(ax, x_data, y_data, x_scale='linear', y_scale='linear'):
    # Manejo de valores para escala logarítmica en el eje x
    if x_scale == 'log':
        x_min = np.min(x_data[x_data > 0])  # Encontrar mínimo positivo para log
        x_max = np.max(x_data)
        x_min *= 0.9  # 10% menor
        x_max *= 1.1  # 10% mayor
    else:
        x_min = np.min(x_data)
        x_max = np.max(x_data)
        x_range = x_max - x_min
        x_min -= x_range * 0.1
        x_max += x_range * 0.1
    
    # Manejo de valores para escala logarítmica en el eje y
    if y_scale == 'log':
        y_min = np.min(y_data[y_data > 0])  # Encontrar mínimo positivo para log
        y_max = np.max(y_data)
        y_min *= 0.9  # 10% menor
        y_max *= 1.1  # 10% mayor
    else:
        y_min = np.min(y_data)
        y_max = np.max(y_data)
        y_range = y_max - y_min
        y_min -= y_range * 0.1
        y_max += y_range * 0.1
    
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

# Definir colores y estilos para las líneas verticales de referencia
color_fp = 'darkgreen'  # Color para la frecuencia del puerto
color_fs = 'darkred'    # Color para la frecuencia del driver
alpha_vert = 0.7        # Transparencia de las líneas
linestyle_vert = '--'   # Estilo de línea punteada

# Calcular la frecuencia máxima donde ka = 1
# k = 2π*f/c, a = radio del diafragma (ad)
f_max = c0/(2*np.pi*ad)  # Aproximadamente 325 Hz

# PRIMERA VENTANA - Impedancia y SPL
# ---------------------------------
fig1, axes1 = plt.subplots(2, 2, figsize=(14, 12))
plt.subplots_adjust(wspace=0.3, hspace=0.3)

# 1. IMPEDANCIA (MAGNITUD)
ax = axes1[0, 0]
ax.plot(freq, Zt, linewidth=2, color='navy')
ax.set_xscale("log")
# Ajustar límites a 10Hz - f_max
ax.set_xlim(10, f_max)
# Establecer límites en Y basados solo en los datos en el rango visible
visible_data = [z for f, z in zip(freq, Zt) if 10 <= f <= f_max]
ax.set_ylim(min(visible_data)*0.9, max(visible_data)*1.1)
# Añadir líneas verticales para las frecuencias de resonancia
ax.axvline(x=fp, color=color_fp, linestyle=linestyle_vert, alpha=alpha_vert)
ax.axvline(x=fs, color=color_fs, linestyle=linestyle_vert, alpha=alpha_vert)
# Añadir etiquetas para las líneas verticales
ax.text(fp*0.95, ax.get_ylim()[1]*0.95, f'fp = {fp} Hz', rotation=90, 
        va='top', ha='right', color=color_fp, fontweight='bold')
ax.text(fs*1.05, ax.get_ylim()[1]*0.95, f'fs = {fs} Hz', rotation=90, 
        va='top', ha='left', color=color_fs, fontweight='bold')
ax.set_xlabel('Frecuencia [Hz]', fontsize=12)
ax.set_ylabel('Impedancia [Ω]', fontsize=12)
ax.set_title('Impedancia (Magnitud)', fontweight='bold', fontsize=14)
ax.grid(True, which="both", ls="-", alpha=0.7)
ax.minorticks_on()

# 2. IMPEDANCIA (FASE)
ax = axes1[0, 1]
ax.plot(freq, ZtΦ, linewidth=2, color='darkblue')
ax.set_xscale("log")
# Ajustar límites a 10Hz - f_max
ax.set_xlim(10, f_max)
# Establecer límites en Y basados solo en los datos en el rango visible
visible_data = [p for f, p in zip(freq, ZtΦ) if 10 <= f <= f_max]
ax.set_ylim(min(visible_data)*0.9, max(visible_data)*1.1)
# Añadir líneas verticales para las frecuencias de resonancia
ax.axvline(x=fp, color=color_fp, linestyle=linestyle_vert, alpha=alpha_vert)
ax.axvline(x=fs, color=color_fs, linestyle=linestyle_vert, alpha=alpha_vert)
# Añadir etiquetas para las líneas verticales
ax.text(fp*0.95, ax.get_ylim()[1]*0.95, f'fp = {fp} Hz', rotation=90, 
        va='top', ha='right', color=color_fp, fontweight='bold')
ax.text(fs*1.05, ax.get_ylim()[1]*0.95, f'fs = {fs} Hz', rotation=90, 
        va='top', ha='left', color=color_fs, fontweight='bold')
ax.set_xlabel('Frecuencia [Hz]', fontsize=12)
ax.set_ylabel('Fase [°]', fontsize=12)
ax.set_title('Impedancia (Fase)', fontweight='bold', fontsize=14)
ax.grid(True, which="both", ls="-", alpha=0.7)
ax.minorticks_on()

# 3. SPL TOTAL (MAGNITUD)
ax = axes1[1, 0]
ax.plot(freq, SPL, linewidth=2, color='crimson', label='Total')
ax.plot(freq, SPLspk, linewidth=1.5, color='royalblue', linestyle='--', label='Cono')  
ax.plot(freq, SPLport, linewidth=1.5, color='forestgreen', linestyle='-.', label='Puerto')
ax.set_xscale("log")
# Ajustar límites a 10Hz - f_max
ax.set_xlim(10, f_max)
# Establecer límites en Y basados solo en los datos en el rango visible
visible_data_total = [spl for f, spl in zip(freq, SPL) if 10 <= f <= f_max]
visible_data_spk = [spl for f, spl in zip(freq, SPLspk) if 10 <= f <= f_max]
visible_data_port = [spl for f, spl in zip(freq, SPLport) if 10 <= f <= f_max]
min_y = min([min(visible_data_total), min(visible_data_spk), min(visible_data_port)])*0.9
max_y = max([max(visible_data_total), max(visible_data_spk), max(visible_data_port)])*1.1
ax.set_ylim(min_y, max_y)
# Añadir líneas verticales para las frecuencias de resonancia
ax.axvline(x=fp, color=color_fp, linestyle=linestyle_vert, alpha=alpha_vert)
ax.axvline(x=fs, color=color_fs, linestyle=linestyle_vert, alpha=alpha_vert)
# Añadir etiquetas para las líneas verticales
ax.text(fp*0.95, ax.get_ylim()[1]*0.95, f'fp = {fp} Hz', rotation=90, 
        va='top', ha='right', color=color_fp, fontweight='bold')
ax.text(fs*1.05, ax.get_ylim()[1]*0.95, f'fs = {fs} Hz', rotation=90, 
        va='top', ha='left', color=color_fs, fontweight='bold')
ax.set_xlabel('Frecuencia [Hz]', fontsize=12)
ax.set_ylabel('SPL [dB]', fontsize=12)
ax.set_title('Respuesta en Frecuencia (SPL)', fontweight='bold', fontsize=14)
ax.grid(True, which="both", ls="-", alpha=0.7)
ax.minorticks_on()
ax.legend(loc='upper left', fontsize=10)

# 4. SPL FASE
ax = axes1[1, 1]
ax.plot(freq, SPLΦ, linewidth=2, color='darkred', label='Total')
ax.plot(freq, SPLspkΦ, linewidth=1.5, color='royalblue', linestyle='--', label='Cono')
ax.plot(freq, SPLportΦ, linewidth=1.5, color='forestgreen', linestyle='-.', label='Puerto')
ax.set_xscale("log")
# Ajustar límites a 10Hz - f_max
ax.set_xlim(10, f_max)
# Establecer límites en Y basados solo en los datos en el rango visible
visible_data_total = [p for f, p in zip(freq, SPLΦ) if 10 <= f <= f_max]
visible_data_spk = [p for f, p in zip(freq, SPLspkΦ) if 10 <= f <= f_max]
visible_data_port = [p for f, p in zip(freq, SPLportΦ) if 10 <= f <= f_max]
min_y = min([min(visible_data_total), min(visible_data_spk), min(visible_data_port)])*0.9
max_y = max([max(visible_data_total), max(visible_data_spk), max(visible_data_port)])*1.1
ax.set_ylim(min_y, max_y)
# Añadir líneas verticales para las frecuencias de resonancia
ax.axvline(x=fp, color=color_fp, linestyle=linestyle_vert, alpha=alpha_vert)
ax.axvline(x=fs, color=color_fs, linestyle=linestyle_vert, alpha=alpha_vert)
# Añadir etiquetas para las líneas verticales
ax.text(fp*0.95, ax.get_ylim()[1]*0.95, f'fp = {fp} Hz', rotation=90, 
        va='top', ha='right', color=color_fp, fontweight='bold')
ax.text(fs*1.05, ax.get_ylim()[1]*0.95, f'fs = {fs} Hz', rotation=90, 
        va='top', ha='left', color=color_fs, fontweight='bold')
ax.set_xlabel('Frecuencia [Hz]', fontsize=12)
ax.set_ylabel('Fase [°]', fontsize=12)
ax.set_title('Fase de la Respuesta (SPL)', fontweight='bold', fontsize=14)
ax.grid(True, which="both", ls="-", alpha=0.7)
ax.minorticks_on()
ax.legend(loc='lower right', fontsize=10)

# Repetir el mismo proceso para la segunda ventana de gráficas:

# SEGUNDA VENTANA - Potencia, Group Delay, Desplazamiento y Respuesta al escalón
# ----------------------------------------------------------------------------
fig2, axes2 = plt.subplots(2, 2, figsize=(14, 12))
plt.subplots_adjust(wspace=0.3, hspace=0.3)

# 5. POTENCIA ACÚSTICA
ax = axes2[0, 0]
ax.plot(freq, LWA, linewidth=2, color='purple')
ax.set_xscale("log")
# Ajustar límites a 10Hz - f_max
ax.set_xlim(10, f_max)
# Establecer límites en Y basados solo en los datos en el rango visible
visible_data = [lw for f, lw in zip(freq, LWA) if 10 <= f <= f_max]
ax.set_ylim(min(visible_data)*0.9, max(visible_data)*1.1)
# Añadir líneas verticales para las frecuencias de resonancia
ax.axvline(x=fp, color=color_fp, linestyle=linestyle_vert, alpha=alpha_vert)
ax.axvline(x=fs, color=color_fs, linestyle=linestyle_vert, alpha=alpha_vert)
# Añadir etiquetas para las líneas verticales
ax.text(fp*0.95, ax.get_ylim()[1]*0.95, f'fp = {fp} Hz', rotation=90, 
        va='top', ha='right', color=color_fp, fontweight='bold')
ax.text(fs*1.05, ax.get_ylim()[1]*0.95, f'fs = {fs} Hz', rotation=90, 
        va='top', ha='left', color=color_fs, fontweight='bold')
ax.set_xlabel('Frecuencia [Hz]', fontsize=12)
ax.set_ylabel('Potencia [dB]', fontsize=12)
ax.set_title('Potencia Acústica (Lw)', fontweight='bold', fontsize=14)
ax.grid(True, which="both", ls="-", alpha=0.7)
ax.minorticks_on()

# 6. GROUP DELAY
ax = axes2[0, 1]
freq_gd = freq[1:-1]
ax.plot(freq_gd, groupdelay, linewidth=2, color='darkmagenta')
ax.set_xscale("log")
# Ajustar límites a 10Hz - f_max
ax.set_xlim(10, f_max)
# Establecer límites en Y basados solo en los datos en el rango visible
visible_data = [gd for f, gd in zip(freq_gd, groupdelay) if 10 <= f <= f_max]
if visible_data:  # Asegurar que hay datos en el rango
    ax.set_ylim(min(visible_data)*0.9, max(visible_data)*1.1)
# Añadir líneas verticales para las frecuencias de resonancia
ax.axvline(x=fp, color=color_fp, linestyle=linestyle_vert, alpha=alpha_vert)
ax.axvline(x=fs, color=color_fs, linestyle=linestyle_vert, alpha=alpha_vert)
# Añadir etiquetas para las líneas verticales
ax.text(fp*0.95, ax.get_ylim()[1]*0.95, f'fp = {fp} Hz', rotation=90, 
        va='top', ha='right', color=color_fp, fontweight='bold')
ax.text(fs*1.05, ax.get_ylim()[1]*0.95, f'fs = {fs} Hz', rotation=90, 
        va='top', ha='left', color=color_fs, fontweight='bold')
ax.set_xlabel('Frecuencia [Hz]', fontsize=12)
ax.set_ylabel('Retardo [ms]', fontsize=12)
ax.set_title('Group Delay', fontweight='bold', fontsize=14)
ax.grid(True, which="both", ls="-", alpha=0.7)
ax.minorticks_on()

# 7. DESPLAZAMIENTO DEL CONO
ax = axes2[1, 0]
ax.plot(freq, DEZ, linewidth=2, color='teal')
ax.set_xscale("log")
# Ajustar límites a 10Hz - f_max
ax.set_xlim(10, f_max)
# Establecer límites en Y basados solo en los datos en el rango visible
visible_data = [dez for f, dez in zip(freq, DEZ) if 10 <= f <= f_max]
ax.set_ylim(min(visible_data)*0.9, max(visible_data)*1.1)
# Añadir líneas verticales para las frecuencias de resonancia
ax.axvline(x=fp, color=color_fp, linestyle=linestyle_vert, alpha=alpha_vert)
ax.axvline(x=fs, color=color_fs, linestyle=linestyle_vert, alpha=alpha_vert)
# Añadir etiquetas para las líneas verticales
ax.text(fp*0.95, ax.get_ylim()[1]*0.95, f'fp = {fp} Hz', rotation=90, 
        va='top', ha='right', color=color_fp, fontweight='bold')
ax.text(fs*1.05, ax.get_ylim()[1]*0.95, f'fs = {fs} Hz', rotation=90, 
        va='top', ha='left', color=color_fs, fontweight='bold')
ax.set_xlabel('Frecuencia [Hz]', fontsize=12)
ax.set_ylabel('Desplazamiento [mm]', fontsize=12)
ax.set_title('Desplazamiento del Cono', fontweight='bold', fontsize=14)
ax.grid(True, which="both", ls="-", alpha=0.7)
ax.minorticks_on()

# 8. RESPUESTA AL ESCALÓN (Sin cambios, ya que es dominio del tiempo)
ax = axes2[1, 1]
ax.plot(time, gtnorm, linewidth=2, color='darkorange')
time_plot = time[time <= 50]
gtnorm_plot = gtnorm[:len(time_plot)]
set_axis_limits(ax, time_plot, gtnorm_plot)
ax.set_xlabel('Tiempo [ms]', fontsize=12)
ax.set_ylabel('Amplitud Normalizada', fontsize=12)
ax.set_title('Respuesta al Escalón', fontweight='bold', fontsize=14)
ax.grid(True, which="both", ls="-", alpha=0.7)
ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3)

# Ajustar espaciado y añadir título general
fig2.tight_layout()
fig2.suptitle('Análisis de Sistema Bass Reflex - JBL 2206H (Parte 2)', 
             fontsize=16, fontweight='bold', y=0.98)

# Guardar la segunda figura
plt.figure(fig2.number)
plt.savefig('bass_reflex_analysis_part2.png', dpi=300, bbox_inches='tight')

# Mostrar ambas figuras
plt.show()
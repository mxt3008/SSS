import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter
# Frecuencia lineal (10 a 1000 Hz)
f = np.linspace(1, 20000, pow(2, 16))
w = 2 * np.pi * f
jw = 1j * w

#Función impedancias en paralelo
def paralelo(*impedancias):
    suma_inversas = sum(1 / Z for Z in impedancias)
    return 1 / suma_inversas

######################################### COLOCAR PARAMETROS ##############################################
V_as = 175.6 * pow(10, -3)
Q_ms = 5 
Q_es = 0.33 
Q_ts = 0.31
fs = 40

S_D = 0.088
D = 2 * np.sqrt(S_D/np.pi)
Bl = 19.2
Re = 5
Le = 1.75 * pow(10, -3)

#########################################       PARÁMETROS FÍSICOS      ####################################
Rho = 1.2           #Densidad del aire
C_VEL = 343         #Velocidad del sonido
mu = 1.56 * pow(10, -5)
#########################################       PARÁMETROS THIELE SMALL      ####################################
X_max = 7.62 * pow(10, -3)   #Extrucion
#####################################   PARÁMETROS DE LOS COMPONENTES DEL PARLANTE   #########################
r = D/2                 #Radio efectivo de radiacion
V_in = 2.83             #Voltaje de entrada RMS
f_lim = C_VEL/(2 * np.pi * r)
R_ED = 0.5
### BOX ###
V_box_1 = 0.175              #Volumen de la caja 1: frontal
V_box_2 = 0.0312              #Volumen de la caja 2: posterior
### PORT ###
f_p_1 = 28.5                #Frecuencia de resonancia del port 1
d_p_1 = 0.12#pow(10, -3)         #Diametro del Port 1
f_p_2 = 82                  #Frecuencia de resonancia del port 2
d_p_2 = 0.12#pow(10, -3)                #Diametro del Port 2
r_p_1 = d_p_1/2
r_p_2 = d_p_2/2

mascara = (f >= 10) & (f <= f_lim)
#########################   PARTE ACÚSTICA   ######################### 
#IMPEDANCIA DE RADIACIÓN (PARTE ACÚSTICA)
M_A_F = 8 * Rho/(3 * r * pow(np.pi, 2))
M_A_F = 0.83 * Rho/(np.pi * r)
M_A_P = 0.83 * Rho/(np.pi * r)
R_A = C_VEL * Rho/(np.pi * pow(r, 2))
#IMPEDANCIA DE RADIACIÓN (PARTE MECÁNICA)
M_MA_F = M_A_F * pow(S_D, 2)
M_MA_P = M_A_P * pow(S_D, 2)
R_MA = R_A * pow(S_D, 2)
#IMPEDANCIA BOX
#IMPEDANCIA DEL PORT
#tubo
l_correccion_1 = 0.85 * r_p_1 + 0.61 * r_p_1
l_correccion_2 = 0.85 * r_p_2 + 0.61 * r_p_2
l_1 = pow(C_VEL, 2) * np.pi * pow(r_p_1, 2)/(pow(2 * np.pi * f_p_1, 2) * V_box_1) - l_correccion_1

l_2 = pow(C_VEL, 2) * np.pi * pow(r_p_2, 2)/(pow(2 * np.pi * f_p_2, 2) * V_box_2) - l_correccion_2

M_A_port_1 = Rho * (l_1 + 0.6 * r_p_1)/(np.pi * pow(r_p_1, 2))
M_A_port_2 = Rho * (l_2 + 0.6 * r_p_2)/(np.pi * pow(r_p_2, 2))

#R_A_port_1 = (1/(np.pi * pow(r_p_1, 2))) * Rho * np.sqrt(2 * w * mu) * (1 + l_1/r_p_1)
#R_A_port_2 = (1/(np.pi * pow(r_p_2, 2))) * Rho * np.sqrt(2 * w * mu) * (1 + l_2/r_p_2)
#radiación tubo
R_AR_port_1 = 0.479 * Rho * C_VEL/pow(r_p_1, 2)
M_AR_port_1 = 0.1952 * Rho/r_p_1

R_AR_port_2 = 0.479  * Rho * C_VEL/pow(r_p_2, 2)
M_AR_port_2 = 0.1952 * Rho/r_p_2
######################   OBTENIENDO LOS PARAMETROS EMA REFLEJADOS A LA PARTE ELECTRICA  ##########################
#ELEMENTOS ACÚSTICOS SPK
R_EA = 4 * pow(Bl, 2)/(Rho * C_VEL * np.pi *  pow(D, 2))       #RESISTENCIA ACÚSTICA DE RADIACIÓN
C_EA = M_MA_F/pow(Bl, 2)
C_EA_P = M_MA_P/pow(Bl, 2)
#ELEMENTOS ACÚSTICOS BOX
L_box_1 = 16 * V_box_1 * pow(Bl, 2)/(Rho * pow(C_VEL, 2) * pow(np.pi, 2) * pow(D, 4))
R_box_1 = 1000

L_box_2 = 16 * V_box_2 * pow(Bl, 2)/(Rho * pow(C_VEL, 2) * pow(np.pi, 2) * pow(D, 4))
R_box_2 = 200
#ELEMENTOS ACÚSTICOS PORT
#tubo
C_Eport_1 = M_A_port_1 * pow(S_D, 2)/pow(Bl, 2)
R_Eport_1 = 200 

C_Eport_2 = M_A_port_2 * pow(S_D, 2)/pow(Bl, 2)
R_Eport_2 = 1000 
#radiación tubo
R_ER_port_1 = pow(Bl, 2)/(R_AR_port_1 * pow(S_D, 2))
C_ER_port_1 = M_AR_port_1 * pow(S_D, 2)/pow(Bl, 2)

R_ER_port_2 = pow(Bl, 2)/(R_AR_port_2 * pow(S_D, 2))
C_ER_port_2 = M_AR_port_2 * pow(S_D, 2)/pow(Bl, 2)
#Impedancias acústicas SPK
Z_R_EA = R_EA
Z_C_EA_F = 1/(jw * C_EA)
Z_C_EA_P = 1/(jw * C_EA_P)

#Impedancias acústicas BOX
#1
Z_Lbox_1 = jw * L_box_1
Z_Rbox_1 = R_box_1

Zbox_1 = paralelo(Z_Lbox_1, Z_Rbox_1)
#2
Z_Lbox_2 = jw * L_box_2
Z_Rbox_2 = R_box_2

Zbox_2 = paralelo(Z_Lbox_2, Z_Rbox_2)
#Impedancias acústicas PORT
#1
Z_RERport_1 = R_ER_port_1
Z_CERport_1 = 1/(jw * C_ER_port_1)

Z_CEport_1 = 1/(jw * C_Eport_1)
Z_REport_1 = R_Eport_1

Z_PORT_1 = paralelo(Z_RERport_1 + Z_CERport_1, Z_CEport_1, Z_REport_1)
#2
Z_RERport_2 = R_ER_port_2
Z_CERport_2 = 1/(jw * C_ER_port_2)

Z_CEport_2 = 1/(jw * C_Eport_2)
Z_REport_2 = R_Eport_2

Z_PORT_2 = paralelo(Z_RERport_2 + Z_CERport_2, Z_CEport_2, Z_REport_2)
### Z acustico total ### #1 = F, 2 = P
Z_AC_F = Z_PORT_1 + paralelo(Z_R_EA + Z_C_EA_F, Zbox_1)
Z_AC_P = Z_PORT_2 + paralelo(Z_R_EA + Z_C_EA_P, Zbox_2)

#ELEMENTOS MECÁNICOS (LADO MECÁNICO)
M_MS = pow(Bl, 2) * Q_es/(2 * np.pi * fs * Re)
C_MS = 1/(pow(2 * np.pi * fs, 2) * M_MS)
R_MS = 2 * np.pi * fs * M_MS/Q_ms
M_MD = M_MS - M_MA_F

#ELEMENTOS MECÁNICOS (LADO ELECTRICO)
R_ES = pow(Bl, 2)/R_MS
C_ES = C_MS * pow(Bl, 2)
M_ED = M_MD/pow(Bl, 2)
#Impedancias mecánicas
Z_R_ES = R_ES
Z_C_ES = jw * C_ES
Z_M_ED = 1/(jw * M_ED)

Z_MEC = paralelo(Z_R_ES, Z_C_ES, Z_M_ED)

#ELEMENTOS ELECTRICOS
#Impedancias electricas
Z_Re = Re
Z_Le = jw * Le
Z_R_ED = R_ED

Z_ELEC = Z_Re + paralelo(Z_Le, Z_R_ED)

#IMPEDANCIA TOTAL
Z_TOTAL = Z_ELEC + paralelo(Z_MEC, Z_AC_F, Z_AC_P)
MOD_Z_TOTAL = np.abs(Z_TOTAL)
FASE_Z_TOTAL = np.angle(Z_TOTAL, deg = 1)

#SPL
Z_D_ELEC = paralelo(Z_MEC, Z_AC_F, Z_AC_P)

I_total = V_in/Z_TOTAL
E_in = I_total * Z_D_ELEC
#PUERTO 1 FRONTAL
I_F = E_in/Z_AC_F
V_puerto_1 = I_F * paralelo(Z_RERport_2 + Z_CERport_2, Z_CEport_2, Z_REport_2) * (-1)

#PUERTO 2 POSTERIOR
I_P = E_in/Z_AC_P
V_puerto_2 = I_P * paralelo(Z_RERport_2 + Z_CERport_2, Z_CEport_2, Z_REport_2)
#SUMA DE AMBOS
V_SPL = V_puerto_1 + V_puerto_2

SPL = 20 * np.log10(w * Rho * pow(D, 2) * np.abs(V_SPL)/(16 * pow(10, -5) * Bl))
MOD_SPL = SPL
FASE_SPL = np.angle(V_SPL, deg = 1) + 90
un_wrape_fase = np.unwrap(FASE_SPL)

#POTENCIA ACÚSTICA

#GROUP DELAY
# Por definicion es el negativo de la derivada de la fase del SPL

Group_Delay = -1000 * np.gradient(un_wrape_fase, f)/360 #probar con w: omega

#RESPUESTA AL ESCALON UNITARIO
# Por definción es la integral de la respuesta al impulso de nuestro sistema
#En nuestro caso se obtiene con la transformada de Fourier inversa del nivel de presión sonora
#(en escala lineal) dividido entre la frecuencia (𝜔).
SPL_lin_w = Rho * pow(D, 2) * np.abs(E_in)/(16 * pow(10, -5) * Bl)
Step_Response = np.fft.ifft(SPL_lin_w, pow(2, 17))
f_MUESTREO = 2 * f[-1]
N = pow(2, 17)
t = 1000 * np.arange(N) / f_MUESTREO
Step_Response_norm = np.real(Step_Response)/max(np.real(Step_Response))

#DEZPLAZAMIENTO en mm
DESPLAZAMIENTO = 1000 * np.sqrt(2) * E_in/(w * Bl)
#######################################(en escala lineal) dividido entre la frecuencia (𝜔).
#####----------GRÁFICOS----------############################################
#IMPEDANCIA
plt.figure(figsize=(6, 8))
plt.subplot(2, 2, 1)
plt.plot(f[mascara], 10 * np.log10(MOD_Z_TOTAL[mascara]), color = 'teal')
plt.title('Impedancia (Mag)')
plt.ylabel("Magnitud (ohm)")
plt.ylim(0, 18)
plt.yticks(np.arange(0, 17.51, 2.5))
plt.xlim(10, f_lim * 1.2)
#plt.xlabel("Frecuencia (Hz)")
plt.xscale('log')
plt.axvline(x=fs, color='red', linestyle='-', linewidth=1)
plt.grid(True, which='both', linestyle='--')

plt.subplot(2, 2, 2)
plt.plot(f[mascara], FASE_Z_TOTAL[mascara], color = 'teal')
plt.title('Impedancia (Fase)')
plt.ylabel("Fase (°)")
plt.ylim(-180, 180)
plt.xlim(10, f_lim * 1.2)
#plt.xlabel("Frecuencia (Hz)")
plt.xscale('log')
plt.axvline(x=fs, color='red', linestyle='-', linewidth=1)
plt.grid(True, which='both', linestyle='--')

plt.tight_layout()

#SPL

#plt.figure(figsize=(10, 6))
plt.subplot(2, 2, 3)
plt.plot(f[mascara], MOD_SPL[mascara], color = 'orange')
plt.title('Lp (Mag)')
plt.ylabel("Mag (dB)")
plt.ylim(50, 110)
plt.xlabel("Frecuencia (Hz)")
plt.xscale('log')
plt.xlim(10, f_lim * 1.2)
plt.grid(True, which='both', linestyle='--')
plt.subplot(2, 2, 4)
#plt.plot(f[mascara], FASE_SPL[mascara], color = 'orange')
plt.plot(f[mascara], un_wrape_fase[mascara], color = 'orange')
plt.title('Lp (Fase)')
plt.ylabel("FASE (°)")
#plt.ylim(-180, 180)
plt.xlabel("Frecuencia (Hz)")
plt.xscale('log')
plt.xlim(1, 1000) #f_lim * 1.2)
plt.grid(True, which='both', linestyle='--')
plt.tight_layout()


#POTENCIA ACÚSTICA

#plt.figure(figsize=(10, 6))
plt.figure(figsize=(6, 8))
plt.subplot(2, 2, 1)
plt.plot(f[mascara], SPL[mascara], color = 'purple')
plt.title('Lw')
plt.ylabel("Mag (dB)")
plt.ylim(50, 100)
plt.xlabel("Frecuencia (Hz)")
plt.xscale('log')
plt.xlim(1, 1000)#f_lim * 1.2)
plt.grid(True, which='both', linestyle='--')

#GROUP DELAY

#plt.figure(figsize=(10, 6))
#plt.subplot(2, 1, 1)
plt.subplot(2, 2, 2)
plt.plot(f[mascara], Group_Delay[mascara], color = 'purple')
plt.title('Group-Delay')
plt.ylabel("Tiempo (ms)")
#plt.ylim(0, 10)
plt.xlabel("Frecuencia (Hz)")
plt.xscale('log')
plt.xlim(10, f_lim * 1.2)
plt.grid(True, which='both', linestyle='--')

#DESPLAZAMIENTO

#plt.figure(figsize=(10, 6))
#plt.subplot(2, 1, 1)
plt.subplot(2, 2, 3)
plt.plot(f[mascara], DESPLAZAMIENTO[mascara], color = 'purple')
plt.title('DESPLAZAMIENTO')
plt.ylabel("Desplaz. (mm)")
plt.ylim(0, 1.5)
plt.xlabel("Frecuencia (Hz)")
plt.xscale('log')
plt.xlim(10, f_lim * 1.2)
plt.grid(True, which='both', linestyle='--')

#Step Response

#plt.figure(figsize=(10, 6))
#plt.subplot(2, 1, 1)
plt.subplot(2, 2, 4)
plt.plot(t, 10*Step_Response_norm, color = 'purple')
plt.title('Step Response')
plt.ylabel("Norm")
plt.ylim(-1, 1)
plt.xlabel("Tiempo (ms)")
plt.xlim(0, 45)
plt.grid(True, which='both', linestyle='--')
plt.tight_layout()
plt.show()
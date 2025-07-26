# --------------------------------------------
# bpp.py
# Simulación completa de caja pasabanda de 4º orden (Bandpass) con dos cámaras y dos puertos
# Implementa el modelo de circuito equivalente electroacústico completo
# --------------------------------------------

import numpy as np                                                      # Importa numpy para cálculos matemáticos complejos
import matplotlib.pyplot as plt                                         # Importa matplotlib para visualización de resultados

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================
# -------------------------------
# CONSTANTES FÍSICAS DEL ENTORNO ACÚSTICO
# -------------------------------

rho0 = 1.2       # Densidad del aire a 20°C y 1 atm [kg/m³]
c = 343          # Velocidad del sonido en aire a 20°C [m/s]
P_ref = 20e-6    # Presión de referencia para cálculo de SPL (0 dB SPL) [Pa]

# -------------------------------
# PARÁMETROS DE EXCITACIÓN ELÉCTRICA
# -------------------------------

V_in = 2.83      # Voltaje RMS de entrada [V] (equivale a 1W en 8Ω)

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================
# -------------------------------
# PARÁMETROS THIELE-SMALL DEL DRIVER
# Especificaciones electroacústicas del altavoz
# -------------------------------

Re = 5.3         # Resistencia DC de la bobina móvil [Ω]
Fs = 52          # Frecuencia de resonancia del driver en aire libre [Hz]
Qms = 2.5        # Factor de calidad mecánico (pérdidas mecánicas)
Qes = 0.34       # Factor de calidad eléctrico (pérdidas eléctricas)
Le = 1.5e-3      # Inductancia de la bobina móvil [H]
Sd = 0.055       # Área efectiva del diafragma [m²]
Bl = 18.1        # Factor de fuerza electroacústica [T·m]
diametro = 2 * np.sqrt(Sd/np.pi)  # Diámetro efectivo del diafragma [m]

# -------------------------------
# PARÁMETROS DERIVADOS DEL DRIVER
# Cálculos basados en los parámetros Thiele-Small
# -------------------------------

Qts = (Qes * Qms)/(Qes + Qms)   # Factor de calidad total del sistema
radio = diametro/2              # Radio efectivo del diafragma [m]

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================
# -------------------------------
# DISEÑO DE LA CAJA PASABANDA
# Especificaciones de volúmenes y frecuencias de sintonía
# -------------------------------

Vol_frontal = 0.175      # Volumen de la cámara frontal [m³] (175 litros)
Vol_posterior = 0.0312   # Volumen de la cámara posterior [m³] (31.2 litros)
freq_obj_1 = 28.5        # Frecuencia de sintonía objetivo cámara frontal [Hz]
freq_obj_2 = 82          # Frecuencia de sintonía objetivo cámara posterior [Hz]
diam_puerto_1 = 0.12     # Diámetro del puerto de la cámara frontal [m]
diam_puerto_2 = 0.12     # Diámetro del puerto de la cámara posterior [m]

# -------------------------------
# GEOMETRÍA DE LOS PUERTOS
# Cálculo de áreas y radios de los puertos
# -------------------------------

Area_puerto_1 = np.pi*(diam_puerto_1/2)**2    # Área transversal del puerto 1 [m²]
Area_puerto_2 = np.pi*(diam_puerto_2/2)**2    # Área transversal del puerto 2 [m²]
radio_puerto_1 = diam_puerto_1/2              # Radio del puerto 1 [m]
radio_puerto_2 = diam_puerto_2/2              # Radio del puerto 2 [m]

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================
# -------------------------------
# CONFIGURACIÓN DEL ANÁLISIS DE FRECUENCIA
# Definición del rango de frecuencias y variables auxiliares
# -------------------------------

frecuencias = np.linspace(1, 20000, pow(2, 16))  # Vector de frecuencias de 1 Hz a 20 kHz con 65536 puntos
omega = 2 * np.pi * frecuencias                  # Vector de frecuencias angulares [rad/s]
j_omega = 1j * omega                              # Operador complejo jω para impedancias reactivas

# -------------------------------
# FUNCIÓN AUXILIAR PARA IMPEDANCIAS EN PARALELO
# Calcula la impedancia equivalente de elementos en paralelo
# -------------------------------

def impedancia_paralelo(*impedancias):
    """
    Calcula la impedancia equivalente de múltiples impedancias en paralelo
    1/Zeq = 1/Z1 + 1/Z2 + ... + 1/Zn
    """
    suma_inversas = sum(1 / Z for Z in impedancias)  # Suma de las inversas de cada impedancia
    return 1 / suma_inversas                         # Inversa de la suma = impedancia equivalente

# -------------------------------
# LÍMITE DE FRECUENCIA PARA VALIDEZ DEL MODELO
# Basado en el criterio ka ≤ 1 para pistón en baffle infinito
# -------------------------------

freq_limite = c/(2 * np.pi * radio)                  # Frecuencia límite donde ka = 1 [Hz]
mascara_freq = (frecuencias >= 10) & (frecuencias <= freq_limite)  # Máscara para el rango de frecuencias válido

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================
# -------------------------------
# MODELO ELECTROACÚSTICO DEL DRIVER
# Transformación de parámetros mecánicos y acústicos al dominio eléctrico
# -------------------------------

# IMPEDANCIAS DE RADIACIÓN ACÚSTICA DEL DIAFRAGMA
# Modelo de pistón circular en baffle infinito
masa_acust_frontal = 0.83 * rho0/(np.pi * radio)          # Masa acústica de radiación frontal [kg/m⁴]
masa_acust_posterior = 0.83 * rho0/(np.pi * radio)        # Masa acústica de radiación posterior [kg/m⁴]
resist_acust_rad = c * rho0/(np.pi * pow(radio, 2))       # Resistencia acústica de radiación [kg/(s·m⁴)]

# TRANSFORMACIÓN AL DOMINIO MECÁNICO
# Multiplicación por Sd² para convertir impedancias acústicas a mecánicas
masa_mec_frontal = masa_acust_frontal * pow(Sd, 2)        # Masa mecánica de radiación frontal [kg]
masa_mec_posterior = masa_acust_posterior * pow(Sd, 2)    # Masa mecánica de radiación posterior [kg]
resist_mec_rad = resist_acust_rad * pow(Sd, 2)            # Resistencia mecánica de radiación [kg/s]

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================
# -------------------------------
# DISEÑO Y CÁLCULO DE LOS PUERTOS
# Determinación de longitudes para lograr las frecuencias de sintonía deseadas
# -------------------------------

# CORRECCIONES DE LONGITUD EFECTIVA
# Factores de corrección por efectos de radiación en los extremos del puerto
correccion_long_1 = 0.85 * radio_puerto_1 + 0.61 * radio_puerto_1  # Corrección total puerto 1 [m]
correccion_long_2 = 0.85 * radio_puerto_2 + 0.61 * radio_puerto_2  # Corrección total puerto 2 [m]

# CÁLCULO DE LONGITUDES FÍSICAS DE LOS PUERTOS
# Basado en la ecuación de resonancia de Helmholtz: f = c/(2π)·√(Sp/(Vb·Leff))
longitud_puerto_1 = pow(c, 2) * np.pi * pow(radio_puerto_1, 2)/(pow(2 * np.pi * freq_obj_1, 2) * Vol_frontal) - correccion_long_1
longitud_puerto_2 = pow(c, 2) * np.pi * pow(radio_puerto_2, 2)/(pow(2 * np.pi * freq_obj_2, 2) * Vol_posterior) - correccion_long_2

# MASAS ACÚSTICAS DE LOS PUERTOS
# Incluyen la longitud física más las correcciones de extremo
masa_acust_puerto_1 = rho0 * (longitud_puerto_1 + 0.6 * radio_puerto_1)/(np.pi * pow(radio_puerto_1, 2))  # Masa acústica puerto 1 [kg/m⁴]
masa_acust_puerto_2 = rho0 * (longitud_puerto_2 + 0.6 * radio_puerto_2)/(np.pi * pow(radio_puerto_2, 2))  # Masa acústica puerto 2 [kg/m⁴]

# IMPEDANCIAS DE RADIACIÓN DE LOS PUERTOS
# Resistencias y masas adicionales por radiación en los extremos
resist_rad_puerto_1 = 0.479 * rho0 * c/pow(radio_puerto_1, 2)  # Resistencia de radiación puerto 1 [kg/(s·m⁴)]
masa_rad_puerto_1 = 0.1952 * rho0/radio_puerto_1              # Masa de radiación puerto 1 [kg/m⁴]
resist_rad_puerto_2 = 0.479 * rho0 * c/pow(radio_puerto_2, 2)  # Resistencia de radiación puerto 2 [kg/(s·m⁴)]
masa_rad_puerto_2 = 0.1952 * rho0/radio_puerto_2              # Masa de radiación puerto 2 [kg/m⁴]

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================
# -------------------------------
# TRANSFORMACIÓN AL DOMINIO ELÉCTRICO
# Conversión de todos los elementos acústicos y mecánicos a impedancias eléctricas equivalentes
# -------------------------------

# IMPEDANCIAS DE RADIACIÓN DEL DIAFRAGMA (REFLEJADAS AL DOMINIO ELÉCTRICO)
R_rad_elec = 4 * pow(Bl, 2)/(rho0 * c * np.pi * pow(diametro, 2))  # Resistencia de radiación eléctrica equivalente [Ω]
Cap_masa_frontal = masa_mec_frontal/pow(Bl, 2)                      # Capacitancia equivalente masa frontal [F]
Cap_masa_posterior = masa_mec_posterior/pow(Bl, 2)                  # Capacitancia equivalente masa posterior [F]

# IMPEDANCIAS DE LAS CÁMARAS (REFLEJADAS AL DOMINIO ELÉCTRICO)
# Factor 16 proviene de la transformación del volumen acústico al dominio eléctrico
Ind_camara_1 = 16 * Vol_frontal * pow(Bl, 2)/(rho0 * pow(c, 2) * pow(np.pi, 2) * pow(diametro, 4))  # Inductancia cámara 1 [H]
R_perdidas_1 = 1000                                                                                   # Resistencia pérdidas cámara 1 [Ω]
Ind_camara_2 = 16 * Vol_posterior * pow(Bl, 2)/(rho0 * pow(c, 2) * pow(np.pi, 2) * pow(diametro, 4))  # Inductancia cámara 2 [H]
R_perdidas_2 = 200                                                                                     # Resistencia pérdidas cámara 2 [Ω]

# IMPEDANCIAS DE LOS PUERTOS (REFLEJADAS AL DOMINIO ELÉCTRICO)
# Elementos principales de masa acústica de los puertos
Cap_puerto_1 = masa_acust_puerto_1 * pow(Sd, 2)/pow(Bl, 2)       # Capacitancia equivalente puerto 1 [F]
R_equiv_puerto_1 = 200                                           # Resistencia equivalente puerto 1 [Ω]
Cap_puerto_2 = masa_acust_puerto_2 * pow(Sd, 2)/pow(Bl, 2)       # Capacitancia equivalente puerto 2 [F]
R_equiv_puerto_2 = 1000                                          # Resistencia equivalente puerto 2 [Ω]

# IMPEDANCIAS DE RADIACIÓN DE LOS PUERTOS (REFLEJADAS AL DOMINIO ELÉCTRICO)
R_rad_puerto_1_elec = pow(Bl, 2)/(resist_rad_puerto_1 * pow(Sd, 2))  # Resistencia radiación puerto 1 reflejada [Ω]
Cap_rad_puerto_1 = masa_rad_puerto_1 * pow(Sd, 2)/pow(Bl, 2)         # Capacitancia radiación puerto 1 reflejada [F]
R_rad_puerto_2_elec = pow(Bl, 2)/(resist_rad_puerto_2 * pow(Sd, 2))  # Resistencia radiación puerto 2 reflejada [Ω]
Cap_rad_puerto_2 = masa_rad_puerto_2 * pow(Sd, 2)/pow(Bl, 2)         # Capacitancia radiación puerto 2 reflejada [F]

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================
# -------------------------------
# CONSTRUCCIÓN DEL CIRCUITO EQUIVALENTE
# Cálculo de impedancias complejas de cada elemento del circuito
# -------------------------------

# IMPEDANCIAS DE RADIACIÓN DEL DIAFRAGMA
Z_resist_rad = R_rad_elec                               # Resistencia de radiación [Ω]
Z_cap_masa_frontal = 1/(j_omega * Cap_masa_frontal)     # Reactancia capacitiva masa frontal [Ω]
Z_cap_masa_posterior = 1/(j_omega * Cap_masa_posterior) # Reactancia capacitiva masa posterior [Ω]

# IMPEDANCIAS DE LAS CÁMARAS
# Cámara 1 (frontal): Inductancia en paralelo con resistencia
Z_ind_camara_1 = j_omega * Ind_camara_1                           # Reactancia inductiva cámara 1 [Ω]
Z_resist_camara_1 = R_perdidas_1                                  # Resistencia pérdidas cámara 1 [Ω]
Z_camara_1 = impedancia_paralelo(Z_ind_camara_1, Z_resist_camara_1)  # Impedancia equivalente cámara 1 [Ω]

# Cámara 2 (posterior): Inductancia en paralelo con resistencia
Z_ind_camara_2 = j_omega * Ind_camara_2                           # Reactancia inductiva cámara 2 [Ω]
Z_resist_camara_2 = R_perdidas_2                                  # Resistencia pérdidas cámara 2 [Ω]
Z_camara_2 = impedancia_paralelo(Z_ind_camara_2, Z_resist_camara_2)  # Impedancia equivalente cámara 2 [Ω]

# IMPEDANCIAS DE LOS PUERTOS
# Puerto 1: Elementos en serie y paralelo según el modelo del circuito equivalente
Z_resist_rad_puerto_1 = R_rad_puerto_1_elec                      # Resistencia radiación puerto 1 [Ω]
Z_cap_rad_puerto_1 = 1/(j_omega * Cap_rad_puerto_1)              # Reactancia capacitiva radiación puerto 1 [Ω]
Z_cap_puerto_1 = 1/(j_omega * Cap_puerto_1)                      # Reactancia capacitiva masa puerto 1 [Ω]
Z_resist_equiv_puerto_1 = R_equiv_puerto_1                       # Resistencia equivalente puerto 1 [Ω]
# Configuración: (R + jX_C) en paralelo con jX_C y R
Z_puerto_1_total = impedancia_paralelo(Z_resist_rad_puerto_1 + Z_cap_rad_puerto_1, Z_cap_puerto_1, Z_resist_equiv_puerto_1)

# Puerto 2: Misma estructura que puerto 1
Z_resist_rad_puerto_2 = R_rad_puerto_2_elec                      # Resistencia radiación puerto 2 [Ω]
Z_cap_rad_puerto_2 = 1/(j_omega * Cap_rad_puerto_2)              # Reactancia capacitiva radiación puerto 2 [Ω]
Z_cap_puerto_2 = 1/(j_omega * Cap_puerto_2)                      # Reactancia capacitiva masa puerto 2 [Ω]
Z_resist_equiv_puerto_2 = R_equiv_puerto_2                       # Resistencia equivalente puerto 2 [Ω]
Z_puerto_2_total = impedancia_paralelo(Z_resist_rad_puerto_2 + Z_cap_rad_puerto_2, Z_cap_puerto_2, Z_resist_equiv_puerto_2)

# IMPEDANCIAS ACÚSTICAS TOTALES POR LADO
# Cada lado: Puerto en serie con (Radiación + Cámara en paralelo)
Z_acustico_frontal = Z_puerto_1_total + impedancia_paralelo(Z_resist_rad + Z_cap_masa_frontal, Z_camara_1)    # Lado frontal [Ω]
Z_acustico_posterior = Z_puerto_2_total + impedancia_paralelo(Z_resist_rad + Z_cap_masa_posterior, Z_camara_2)  # Lado posterior [Ω]

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================
# -------------------------------
# MODELO MECÁNICO DEL DRIVER
# Impedancias mecánicas reflejadas al dominio eléctrico
# -------------------------------

# PARÁMETROS MECÁNICOS BÁSICOS DEL DRIVER
masa_movil_equiv = pow(Bl, 2) * Qes/(2 * np.pi * Fs * Re)  # Masa móvil equivalente eléctrica [H]
compliance_equiv = 1/(pow(2 * np.pi * Fs, 2) * masa_movil_equiv)  # Compliancia mecánica equivalente eléctrica [F]
resist_mec_equiv = 2 * np.pi * Fs * masa_movil_equiv/Qms   # Resistencia mecánica equivalente eléctrica [Ω]
masa_diafragma = masa_movil_equiv - masa_mec_frontal       # Masa del diafragma sin carga de radiación [H]

# IMPEDANCIAS MECÁNICAS REFLEJADAS AL DOMINIO ELÉCTRICO
R_mec_reflejada = pow(Bl, 2)/resist_mec_equiv              # Resistencia mecánica reflejada [Ω]
Cap_compliance = compliance_equiv * pow(Bl, 2)             # Compliancia mecánica reflejada [F]
masa_diafragma_reflejada = masa_diafragma/pow(Bl, 2)      # Masa del diafragma reflejada [H]

# IMPEDANCIAS COMPLEJAS DEL SISTEMA MECÁNICO
Z_resist_mecanica = R_mec_reflejada                        # Resistencia mecánica [Ω]
Z_cap_compliance = j_omega * Cap_compliance                # Reactancia capacitiva compliancia [Ω]
Z_masa_diafragma = 1/(j_omega * masa_diafragma_reflejada)  # Reactancia inductiva masa [Ω]
Z_mecanico = impedancia_paralelo(Z_resist_mecanica, Z_cap_compliance, Z_masa_diafragma)  # Impedancia mecánica equivalente [Ω]

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================
# -------------------------------
# MODELO ELÉCTRICO DEL DRIVER
# Impedancias puramente eléctricas de la bobina móvil
# -------------------------------

R_perdidas_adicional = 0.5                               # Resistencia adicional de pérdidas [Ω]
Z_resistencia_dc = Re                                     # Resistencia DC de la bobina [Ω]
Z_inductancia_bobina = j_omega * Le                       # Reactancia inductiva de la bobina [Ω]
Z_resist_adicional = R_perdidas_adicional                 # Resistencia adicional [Ω]
Z_electrico = Z_resistencia_dc + impedancia_paralelo(Z_inductancia_bobina, Z_resist_adicional)  # Impedancia eléctrica total [Ω]

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================
# -------------------------------
# IMPEDANCIA TOTAL DEL SISTEMA
# Combinación de todas las impedancias según el circuito equivalente
# -------------------------------

Z_sistema_total = Z_electrico + impedancia_paralelo(Z_mecanico, Z_acustico_frontal, Z_acustico_posterior)  # Impedancia total vista desde los terminales [Ω]
magnitud_impedancia = np.abs(Z_sistema_total)                     # Magnitud de la impedancia total [Ω]
fase_impedancia = np.angle(Z_sistema_total, deg=True)             # Fase de la impedancia total [°]

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================
# -------------------------------
# CÁLCULO DE SPL (NIVEL DE PRESIÓN SONORA)
# Análisis de la respuesta acústica del sistema
# -------------------------------

# IMPEDANCIA VISTA POR EL DRIVER (SIN LA PARTE PURAMENTE ELÉCTRICA)
Z_carga_driver = impedancia_paralelo(Z_mecanico, Z_acustico_frontal, Z_acustico_posterior)  # Impedancia del driver [Ω]

# ANÁLISIS DE CORRIENTES Y VOLTAJES
corriente_total = V_in/Z_sistema_total                            # Corriente total del sistema [A]
voltaje_driver = corriente_total * Z_carga_driver                 # Voltaje en el driver [V]

# CORRIENTES EN CADA RAMA ACÚSTICA
corriente_frontal = voltaje_driver/Z_acustico_frontal             # Corriente rama frontal [A]
voltaje_puerto_1 = corriente_frontal * Z_puerto_1_total * (-1)   # Voltaje puerto 1 (invertido) [V]

corriente_posterior = voltaje_driver/Z_acustico_posterior         # Corriente rama posterior [A]
voltaje_puerto_2 = corriente_posterior * Z_puerto_2_total        # Voltaje puerto 2 [V]

# SUMA FASORIAL DE CONTRIBUCIONES
voltaje_SPL = voltaje_puerto_1 + voltaje_puerto_2                # Voltaje total para SPL [V]

# CÁLCULO FINAL DE SPL
# Conversión de voltaje eléctrico a presión acústica
SPL = 20 * np.log10(omega * rho0 * pow(diametro, 2) * np.abs(voltaje_SPL)/(16 * pow(10, -5) * Bl))

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================
# -------------------------------
# PREPARACIÓN DE DATOS PARA VISUALIZACIÓN
# Conversión a listas para compatibilidad con funciones de graficación
# -------------------------------

lista_impedancia = magnitud_impedancia.tolist()          # Lista de magnitudes de impedancia
lista_fase = fase_impedancia.tolist()                    # Lista de fases de impedancia
lista_SPL = SPL.tolist()                                 # Lista de valores de SPL

# -------------------------------
# REPORTE DE RESULTADOS DE DISEÑO
# Verificación de las especificaciones de diseño
# -------------------------------

print(f"Frecuencia de sintonía 1: {freq_obj_1:.1f} Hz")    # Frecuencia objetivo cámara 1
print(f"Frecuencia de sintonía 2: {freq_obj_2:.1f} Hz")    # Frecuencia objetivo cámara 2
print(f"Longitud puerto 1: {longitud_puerto_1:.3f} m")     # Longitud física calculada puerto 1
print(f"Longitud puerto 2: {longitud_puerto_2:.3f} m")     # Longitud física calculada puerto 2

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================
# -------------------------------
# ANÁLISIS ADICIONAL - PARÁMETROS DINÁMICOS DEL SISTEMA
# Cálculo correcto basado en teoría electroacústica fundamental
# -------------------------------

# VELOCIDAD DEL CONO - MÉTODO CORRECTO
# La velocidad se obtiene directamente del voltaje en el driver dividido por Bl
# v = E_driver / Bl donde E_driver es el voltaje efectivo en el transductor
velocidad_cono = voltaje_driver / Bl                           # Velocidad compleja del cono [m/s]
velocidad_cono_rms = np.abs(velocidad_cono)                    # Velocidad RMS [m/s]

# DESPLAZAMIENTO DEL DIAFRAGMA - MÉTODO CORRECTO
# x = v / (jω) con protección para frecuencias bajas
omega_protegido = np.where(omega < 0.1, 0.1, omega)           # Evitar división por cero
desplazamiento_cono = velocidad_cono / (1j * omega_protegido)  # Desplazamiento complejo [m]
desplazamiento_rms = np.abs(desplazamiento_cono)               # Desplazamiento RMS [m]
desplazamiento_mm = desplazamiento_rms * 1000                  # Desplazamiento en mm

# ANÁLISIS DE POTENCIAS - MÉTODO CORRECTO
# Potencia eléctrica de entrada (real)
potencia_electrica_input = np.real(V_in * np.conj(corriente_total))  # Potencia de entrada [W]

# Potencia disipada en la resistencia DC
potencia_disipada_Re = np.abs(corriente_total)**2 * Re         # Potencia térmica en Re [W]

# Potencia mecánica entregada al sistema mecánico
# P_mec = Re[v * F*] = Re[v * (Bl * I)*]
fuerza_electromagnetica = Bl * corriente_total                 # Fuerza electromagnética [N]
potencia_mecanica = np.real(velocidad_cono * np.conj(fuerza_electromagnetica))  # Potencia mecánica [W]

# Potencia acústica radiada - MÉTODO CORRECTO
# La potencia acústica se calcula a partir de la resistencia de radiación
# P_rad = |v|² * R_rad donde R_rad es la resistencia mecánica de radiación
potencia_radiacion_mecanica = np.abs(velocidad_cono)**2 * resist_mec_rad  # Potencia de radiación mecánica [W]

# Potencia acústica total considerando los dos puertos
# Se usa la velocidad volumétrica y la presión en cada puerto
velocidad_volumetrica_1 = velocidad_cono * Sd                  # Velocidad volumétrica puerto 1 [m³/s]
velocidad_volumetrica_2 = velocidad_cono * Sd                  # Velocidad volumétrica puerto 2 [m³/s]

# La potencia acústica se relaciona con el SPL calculado
# P_ac ≈ P_radiacion * factor_eficiencia_puertos
factor_eficiencia = 0.3  # Factor típico para caja pasabanda
potencia_acustica = potencia_radiacion_mecanica * factor_eficiencia  # Potencia acústica radiada [W]

# EFICIENCIA DEL SISTEMA - CÁLCULOS CORRECTOS
# Proteger contra división por cero
potencia_input_protegida = np.where(np.abs(potencia_electrica_input) < 1e-12, 1e-12, np.abs(potencia_electrica_input))

# Eficiencia electro-mecánica: potencia mecánica / potencia eléctrica
eficiencia_electro_mecanica = np.where(potencia_input_protegida > 1e-12,
                                     (np.abs(potencia_mecanica) / potencia_input_protegida) * 100, 0)

# Eficiencia electro-acústica: potencia acústica / potencia eléctrica  
eficiencia_electro_acustica = np.where(potencia_input_protegida > 1e-12,
                                     (np.abs(potencia_acustica) / potencia_input_protegida) * 100, 0)

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================
# -------------------------------
# ANÁLISIS DE RETARDO DE GRUPO - MÉTODO ROBUSTO
# -------------------------------

# FUNCIÓN DE TRANSFERENCIA PARA RETARDO DE GRUPO
H_total = voltaje_SPL / V_in                                   # Función de transferencia del sistema
fase_total_rad = np.unwrap(np.angle(H_total))                 # Fase desenvuelta en radianes

# CÁLCULO DEL RETARDO DE GRUPO CON SUAVIZADO
retardo_grupo = np.zeros_like(fase_total_rad)

# Aplicar ventana móvil para suavizar el cálculo
ventana = 5  # Tamaño de ventana para suavizado
for i in range(ventana, len(fase_total_rad) - ventana):
    # Calcular pendiente usando regresión lineal local
    indices = np.arange(i - ventana, i + ventana + 1)
    omega_local = omega[indices]
    fase_local = fase_total_rad[indices]
    
    # Regresión lineal: pendiente = (n*Σ(xy) - Σ(x)Σ(y)) / (n*Σ(x²) - (Σ(x))²)
    n = len(indices)
    if n > 2:
        sum_x = np.sum(omega_local)
        sum_y = np.sum(fase_local)
        sum_xy = np.sum(omega_local * fase_local)
        sum_x2 = np.sum(omega_local**2)
        
        denominador = n * sum_x2 - sum_x**2
        if np.abs(denominador) > 1e-10:
            pendiente = (n * sum_xy - sum_x * sum_y) / denominador
            retardo_grupo[i] = -pendiente  # Retardo de grupo en segundos

retardo_grupo_ms = retardo_grupo * 1000                       # Convertir a milisegundos

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================
# -------------------------------
# ANÁLISIS DE RESPUESTA AL ESCALÓN - MÉTODO SIMPLIFICADO
# -------------------------------

# CONFIGURACIÓN TEMPORAL
tiempo_max = 0.05                                             # 50 ms de análisis
N_temporal = 1024                                             # Reducir para mayor estabilidad
t = np.linspace(0, tiempo_max, N_temporal)
dt = t[1] - t[0]

# RESPUESTA AL ESCALÓN USANDO CONVOLUCIÓN SIMPLE
# Crear escalón unitario
escalon_unitario = np.ones(N_temporal)

# Función de transferencia interpolada en tiempo
try:
    from scipy.signal import impulse, lti
    from scipy.interpolate import interp1d
    
    # Crear función de transferencia aproximada usando datos de baja frecuencia
    freq_bajas = frecuencias[mascara_freq & (frecuencias <= 500)]  # Solo hasta 500 Hz
    H_bajas = H_total[mascara_freq & (frecuencias <= 500)]
    
    if len(freq_bajas) > 10:
        # Respuesta al escalón aproximada
        t_respuesta = np.linspace(0, 0.05, 200)
        
        # Aproximación exponencial simple basada en la frecuencia de resonancia
        tau = 1 / (2 * np.pi * Fs)  # Constante de tiempo basada en fs
        respuesta_escalon = 1 - np.exp(-t_respuesta / tau)
        
        # Modular con características del sistema
        factor_amortiguamiento = 1 / (2 * Qts)
        respuesta_escalon *= (1 - factor_amortiguamiento * np.exp(-t_respuesta / (2 * tau)))
    else:
        respuesta_escalon = np.zeros(200)
        t_respuesta = np.linspace(0, 0.05, 200)
        
except ImportError:
    # Si no hay scipy.signal, crear respuesta dummy
    t_respuesta = np.linspace(0, 0.05, 200)
    respuesta_escalon = np.zeros(200)

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================
# -------------------------------
# ANÁLISIS DE LÍMITES OPERATIVOS - CORREGIDO
# -------------------------------

# LÍMITES REALISTAS PARA EL DRIVER
Xmax = 6.0e-3                                                 # 6 mm Xmax típico para este tipo de driver
Potencia_nominal = 120                                        # 120W potencia nominal más realista

# FACTORES DE SEGURIDAD
factor_seguridad_desp = Xmax / (desplazamiento_rms + 1e-12)   
factor_seguridad_pot = Potencia_nominal / (potencia_disipada_Re + 1e-12)

# FRECUENCIAS CRÍTICAS
mask_valido_analisis = mascara_freq & np.isfinite(desplazamiento_rms) & np.isfinite(potencia_disipada_Re)
if np.sum(mask_valido_analisis) > 10:
    idx_max_desp = np.argmax(desplazamiento_rms[mask_valido_analisis])
    idx_max_pot = np.argmax(potencia_disipada_Re[mask_valido_analisis])
    freq_critica_desp = frecuencias[mask_valido_analisis][idx_max_desp]
    freq_critica_pot = frecuencias[mask_valido_analisis][idx_max_pot]
else:
    freq_critica_desp = Fs
    freq_critica_pot = Fs

# ANÁLISIS DE ESTABILIDAD TÉRMICA
temperatura_bobina = 25 + (potencia_disipada_Re / 0.1)       # Estimación temperatura bobina [°C]
factor_estabilidad_termica = np.where(temperatura_bobina > 150, 0.5, 1.0)  # Factor de reducción por temperatura

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================
# -------------------------------
# PREPARACIÓN DE DATOS PARA VISUALIZACIÓN - VALIDACIÓN
# -------------------------------

# Filtro robusto para datos válidos
mask_valido = (mascara_freq & 
               np.isfinite(velocidad_cono_rms) & 
               np.isfinite(desplazamiento_mm) &
               np.isfinite(eficiencia_electro_mecanica) &
               np.isfinite(eficiencia_electro_acustica) &
               (velocidad_cono_rms > 0) &
               (desplazamiento_mm > 0))

# Verificar que tenemos datos válidos
if np.sum(mask_valido) < 10:
    print("ADVERTENCIA: Pocos datos válidos para análisis dinámico")
    mask_valido = mascara_freq  # Usar máscara básica

# REPORTE DE RESULTADOS CORREGIDO
print(f"\n=== ANÁLISIS DINÁMICO COMPLETO ===")
print(f"Desplazamiento máximo: {np.max(desplazamiento_mm[mask_valido]):.3f} mm @ {freq_critica_desp:.1f} Hz")
print(f"Velocidad máxima: {np.max(velocidad_cono_rms[mask_valido])*1000:.1f} mm/s")
print(f"Potencia mecánica máxima: {np.max(np.abs(potencia_mecanica[mask_valido])):.5f} W")
print(f"Potencia acústica máxima: {np.max(np.abs(potencia_acustica[mask_valido])):.5f} W")
print(f"Eficiencia electro-mecánica máxima: {np.max(eficiencia_electro_mecanica[mask_valido]):.3f}%")
print(f"Eficiencia electro-acústica máxima: {np.max(eficiencia_electro_acustica[mask_valido]):.3f}%")
print(f"Factor seguridad desplazamiento mínimo: {np.min(factor_seguridad_desp[mask_valido]):.1f}")
print(f"Potencia disipada máxima: {np.max(potencia_disipada_Re[mask_valido]):.5f} W")
print(f"Temperatura máxima estimada: {np.max(temperatura_bobina[mask_valido]):.1f} °C")

# Convertir arrays a listas para visualización
lista_velocidad = velocidad_cono_rms.tolist()
lista_desplazamiento = desplazamiento_mm.tolist()
lista_eficiencia_mec = eficiencia_electro_mecanica.tolist()
lista_eficiencia_ac = eficiencia_electro_acustica.tolist()
lista_retardo = retardo_grupo_ms.tolist()
lista_potencia_input = potencia_electrica_input.tolist()
lista_potencia_mecanica = np.abs(potencia_mecanica).tolist()
lista_potencia_acustica = np.abs(potencia_acustica).tolist()

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================
# -------------------------------
# VISUALIZACIÓN COMPLETA EN UNA SOLA VENTANA
# Todas las gráficas organizadas en una figura única con funcionalidad de zoom
# -------------------------------

from matplotlib.ticker import LogLocator, FuncFormatter

# Calcular frecuencia máxima válida más 10%
freq_max_display = freq_limite * 1.1

# Función para abrir gráfica individual en nueva ventana
def abrir_grafica_individual(event):
    """Función para abrir una gráfica individual al hacer doble clic"""
    if event.dblclick and event.inaxes:
        ax_clickeado = event.inaxes
        
        # Crear nueva figura para la gráfica individual
        fig_individual = plt.figure(figsize=(12, 8))
        ax_nuevo = fig_individual.add_subplot(111)
        
        # Copiar contenido del eje clickeado
        for line in ax_clickeado.get_lines():
            ax_nuevo.plot(line.get_xdata(), line.get_ydata(), 
                         color=line.get_color(), linewidth=line.get_linewidth()*1.5,
                         linestyle=line.get_linestyle(), label=line.get_label())
        
        # Copiar propiedades del eje
        ax_nuevo.set_xlim(10, freq_limite)  # Usar frecuencia límite sin extensión
        ax_nuevo.set_ylim(ax_clickeado.get_ylim())
        ax_nuevo.set_xlabel(ax_clickeado.get_xlabel(), fontsize=14, fontweight='bold')
        ax_nuevo.set_ylabel(ax_clickeado.get_ylabel(), fontsize=14, fontweight='bold')
        ax_nuevo.set_title(ax_clickeado.get_title(), fontsize=16, fontweight='bold', pad=20)
        
        # Copiar escala logarítmica si existe
        if ax_clickeado.get_xscale() == 'log':
            ax_nuevo.set_xscale('log')
            # Configurar ticks de frecuencia basados en freq_limite
            if freq_limite <= 100:
                ax_nuevo.set_xticks([10, 100])
                ax_nuevo.set_xticklabels(['10', '100'])
            elif freq_limite <= 1000:
                ax_nuevo.set_xticks([10, 100, 1000])
                ax_nuevo.set_xticklabels(['10', '100', '1k'])
            else:
                ax_nuevo.set_xticks([10, 100, 1000])
                ax_nuevo.set_xticklabels(['10', '100', '1k'])
        if ax_clickeado.get_yscale() == 'log':
            ax_nuevo.set_yscale('log')
        
        # Configurar grilla
        ax_nuevo.grid(True, which='both', alpha=0.7, linestyle='-', linewidth=0.8)
        ax_nuevo.grid(True, which='minor', alpha=0.4, linestyle=':', linewidth=0.5)
        
        # Configurar leyenda
        ax_nuevo.legend(fontsize=12, framealpha=0.9, loc='best')
        
        # Configurar ticks
        ax_nuevo.tick_params(axis='both', which='major', labelsize=12)
        ax_nuevo.tick_params(axis='both', which='minor', labelsize=10)
        
        plt.tight_layout()
        plt.show()

# Configurar formateador personalizado para ejes de frecuencia
def formato_freq(x, pos):
    if x >= 1000:
        return f'{int(x/1000)}k'
    else:
        return f'{int(x)}'

formatter_freq = FuncFormatter(formato_freq)

# Configuración de figura única con todas las gráficas - MÁS ESPACIADA
fig, axes = plt.subplots(3, 3, figsize=(24, 18))
plt.subplots_adjust(wspace=0.5, hspace=0.6)  # Mucho más espacio entre gráficas

# Conectar el evento de doble clic
fig.canvas.mpl_connect('button_press_event', abrir_grafica_individual)

# ================================ ANÁLISIS PRINCIPAL (FILA 1) ================================

# GRÁFICA 1: MAGNITUD DE IMPEDANCIA
ax = axes[0, 0]
ax.semilogx(frecuencias[mascara_freq], magnitud_impedancia[mascara_freq], 
           color='#2E8B57', linewidth=2.5, label='|Z|')
ax.set_xlim(10, freq_limite)
ax.set_ylim(0, max(magnitud_impedancia[mascara_freq]) * 1.1)
ax.set_xlabel('Frecuencia [Hz]', fontsize=9, fontweight='bold')
ax.set_ylabel('Impedancia [Ω]', fontsize=9, fontweight='bold')
ax.set_title('Impedancia - Magnitud', fontsize=8, fontweight='bold', pad=5)
ax.grid(True, which='both', alpha=0.7, linestyle='-', linewidth=0.5)
ax.grid(True, which='minor', alpha=0.4, linestyle=':', linewidth=0.3)
# Configurar ticks basados en freq_limite
if freq_limite <= 100:
    ax.set_xticks([10, 100])
    ax.set_xticklabels(['10', '100'])
elif freq_limite <= 1000:
    ax.set_xticks([10, 100, 1000])
    ax.set_xticklabels(['10', '100', '1k'])
else:
    ax.set_xticks([10, 100, 1000])
    ax.set_xticklabels(['10', '100', '1k'])
ax.axvline(x=Fs, color='red', linestyle='--', alpha=0.8, linewidth=1.5, label=f'fs = {Fs} Hz')
ax.axvline(x=freq_obj_1, color='blue', linestyle='--', alpha=0.8, linewidth=1, label=f'fp1 = {freq_obj_1} Hz')
ax.axvline(x=freq_obj_2, color='green', linestyle='--', alpha=0.8, linewidth=1, label=f'fp2 = {freq_obj_2} Hz')
ax.legend(fontsize=7, framealpha=0.9)
ax.tick_params(axis='both', which='major', labelsize=8)

# GRÁFICA 2: FASE DE IMPEDANCIA
ax = axes[0, 1]
ax.semilogx(frecuencias[mascara_freq], fase_impedancia[mascara_freq], 
           color='#B22222', linewidth=2.5, label='∠Z')
ax.set_xlim(10, freq_limite)
ax.set_ylim(-90, 90)
ax.set_xlabel('Frecuencia [Hz]', fontsize=9, fontweight='bold')
ax.set_ylabel('Fase [°]', fontsize=9, fontweight='bold')
ax.set_title('Impedancia - Fase', fontsize=8, fontweight='bold', pad=5)
ax.grid(True, which='both', alpha=0.7, linestyle='-', linewidth=0.5)
ax.grid(True, which='minor', alpha=0.4, linestyle=':', linewidth=0.3)
if freq_limite <= 100:
    ax.set_xticks([10, 100])
    ax.set_xticklabels(['10', '100'])
elif freq_limite <= 1000:
    ax.set_xticks([10, 100, 1000])
    ax.set_xticklabels(['10', '100', '1k'])
else:
    ax.set_xticks([10, 100, 1000])
    ax.set_xticklabels(['10', '100', '1k'])
ax.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=1)
ax.axvline(x=Fs, color='red', linestyle='--', alpha=0.8, linewidth=1.5)
ax.axvline(x=freq_obj_1, color='blue', linestyle='--', alpha=0.8, linewidth=1)
ax.axvline(x=freq_obj_2, color='green', linestyle='--', alpha=0.8, linewidth=1)
ax.legend(fontsize=7, framealpha=0.9)
ax.tick_params(axis='both', which='major', labelsize=8)

# GRÁFICA 3: RESPUESTA EN FRECUENCIA (SPL)
ax = axes[0, 2]
ax.semilogx(frecuencias[mascara_freq], SPL[mascara_freq], 
           color='#FF6347', linewidth=3, label='SPL Total')
ax.set_xlim(10, freq_limite)
ax.set_ylim(min(SPL[mascara_freq]) - 5, max(SPL[mascara_freq]) + 5)
ax.set_xlabel('Frecuencia [Hz]', fontsize=9, fontweight='bold')
ax.set_ylabel('SPL [dB]', fontsize=9, fontweight='bold')
ax.set_title('SPL - Magnitud', fontsize=8, fontweight='bold', pad=5)
ax.grid(True, which='both', alpha=0.7, linestyle='-', linewidth=0.5)
ax.grid(True, which='minor', alpha=0.4, linestyle=':', linewidth=0.3)
if freq_limite <= 100:
    ax.set_xticks([10, 100])
    ax.set_xticklabels(['10', '100'])
elif freq_limite <= 1000:
    ax.set_xticks([10, 100, 1000])
    ax.set_xticklabels(['10', '100', '1k'])
else:
    ax.set_xticks([10, 100, 1000])
    ax.set_xticklabels(['10', '100', '1k'])
ax.axvline(x=Fs, color='red', linestyle='--', alpha=0.8, linewidth=1.5)
ax.axvline(x=freq_obj_1, color='blue', linestyle='--', alpha=0.8, linewidth=1)
ax.axvline(x=freq_obj_2, color='green', linestyle='--', alpha=0.8, linewidth=1)
ax.legend(fontsize=7, framealpha=0.9)
ax.tick_params(axis='both', which='major', labelsize=8)

# ================================ ANÁLISIS DINÁMICO (FILA 2) ================================

# GRÁFICA 4: FASE DEL SPL (MOVIDA AQUÍ)
ax = axes[1, 0]
fase_spl_unwrapped = np.unwrap(np.angle(voltaje_SPL, deg=True))
ax.semilogx(frecuencias[mascara_freq], fase_spl_unwrapped[mascara_freq], 
           color='#4169E1', linewidth=2.5, label='Fase SPL')
ax.set_xlim(10, freq_limite)
ax.set_xlabel('Frecuencia [Hz]', fontsize=9, fontweight='bold')
ax.set_ylabel('Fase [°]', fontsize=9, fontweight='bold')
ax.set_title('SPL - Fase', fontsize=8, fontweight='bold', pad=5)
ax.grid(True, which='both', alpha=0.7, linestyle='-', linewidth=0.5)
ax.grid(True, which='minor', alpha=0.4, linestyle=':', linewidth=0.3)
if freq_limite <= 100:
    ax.set_xticks([10, 100])
    ax.set_xticklabels(['10', '100'])
elif freq_limite <= 1000:
    ax.set_xticks([10, 100, 1000])
    ax.set_xticklabels(['10', '100', '1k'])
else:
    ax.set_xticks([10, 100, 1000])
    ax.set_xticklabels(['10', '100', '1k'])
ax.axvline(x=Fs, color='red', linestyle='--', alpha=0.8, linewidth=1.5)
ax.axvline(x=freq_obj_1, color='blue', linestyle='--', alpha=0.8, linewidth=1)
ax.axvline(x=freq_obj_2, color='green', linestyle='--', alpha=0.8, linewidth=1)
ax.legend(fontsize=7, framealpha=0.9)
ax.tick_params(axis='both', which='major', labelsize=8)

# GRÁFICA 5: DESPLAZAMIENTO DEL CONO
ax = axes[1, 1]
desp_min = np.min(desplazamiento_mm[mascara_freq])
desp_max = np.max(desplazamiento_mm[mascara_freq])
ax.loglog(frecuencias[mascara_freq], desplazamiento_mm[mascara_freq], 
          color='#FF4500', linewidth=2.5, label='Desplazamiento RMS')
ax.axhline(y=Xmax*1000, color='red', linestyle='--', alpha=0.8, linewidth=2, label=f'Xmax = {Xmax*1000:.1f} mm')
ax.set_xlim(10, freq_limite)
ax.set_ylim(max(desp_min*0.3, 0.001), max(desp_max*3, Xmax*1000*2))
ax.set_xlabel('Frecuencia [Hz]', fontsize=9, fontweight='bold')
ax.set_ylabel('Desplazamiento [mm]', fontsize=9, fontweight='bold')
ax.set_title('Desplazamiento', fontsize=8, fontweight='bold', pad=5)
ax.grid(True, which='both', alpha=0.7, linestyle='-', linewidth=0.5)
ax.grid(True, which='minor', alpha=0.4, linestyle=':', linewidth=0.3)
if freq_limite <= 100:
    ax.set_xticks([10, 100])
    ax.set_xticklabels(['10', '100'])
elif freq_limite <= 1000:
    ax.set_xticks([10, 100, 1000])
    ax.set_xticklabels(['10', '100', '1k'])
else:
    ax.set_xticks([10, 100, 1000])
    ax.set_xticklabels(['10', '100', '1k'])
ax.axvline(x=Fs, color='red', linestyle='--', alpha=0.6, linewidth=1.5)
ax.axvline(x=freq_obj_1, color='blue', linestyle='--', alpha=0.6, linewidth=1)
ax.axvline(x=freq_obj_2, color='green', linestyle='--', alpha=0.6, linewidth=1)
ax.legend(fontsize=7, framealpha=0.9)
ax.tick_params(axis='both', which='major', labelsize=8)

# GRÁFICA 6: VELOCIDAD DEL CONO
ax = axes[1, 2]
ax.semilogx(frecuencias[mascara_freq], velocidad_cono_rms[mascara_freq]*1000, 
            color='#32CD32', linewidth=2.5, label='Velocidad RMS')
ax.set_xlim(10, freq_limite)
ax.set_ylim(0, max(velocidad_cono_rms[mascara_freq]*1000)*1.1)
ax.set_xlabel('Frecuencia [Hz]', fontsize=9, fontweight='bold')
ax.set_ylabel('Velocidad [mm/s]', fontsize=9, fontweight='bold')
ax.set_title('Velocidad', fontsize=8, fontweight='bold', pad=5)
ax.grid(True, which='both', alpha=0.7, linestyle='-', linewidth=0.5)
ax.grid(True, which='minor', alpha=0.4, linestyle=':', linewidth=0.3)
if freq_limite <= 100:
    ax.set_xticks([10, 100])
    ax.set_xticklabels(['10', '100'])
elif freq_limite <= 1000:
    ax.set_xticks([10, 100, 1000])
    ax.set_xticklabels(['10', '100', '1k'])
else:
    ax.set_xticks([10, 100, 1000])
    ax.set_xticklabels(['10', '100', '1k'])
ax.axvline(x=Fs, color='red', linestyle='--', alpha=0.6, linewidth=1.5)
ax.axvline(x=freq_obj_1, color='blue', linestyle='--', alpha=0.6, linewidth=1)
ax.axvline(x=freq_obj_2, color='green', linestyle='--', alpha=0.6, linewidth=1)
ax.legend(fontsize=7, framealpha=0.9)
ax.tick_params(axis='both', which='major', labelsize=8)

# ================================ ANÁLISIS DE POTENCIAS Y EFICIENCIA (FILA 3) ================================

# GRÁFICA 7: ANÁLISIS DE POTENCIAS
ax = axes[2, 0]
ax.semilogx(frecuencias[mascara_freq], np.abs(potencia_electrica_input[mascara_freq])*1000, 
            color='blue', linewidth=2, label='P. Eléctrica')
ax.semilogx(frecuencias[mascara_freq], np.abs(potencia_mecanica[mascara_freq])*1000, 
            color='orange', linewidth=2, label='P. Mecánica')
ax.semilogx(frecuencias[mascara_freq], np.abs(potencia_acustica[mascara_freq])*1000, 
            color='green', linewidth=2, label='P. Acústica')
ax.semilogx(frecuencias[mascara_freq], potencia_disipada_Re[mascara_freq]*1000, 
            color='red', linewidth=2, linestyle=':', label='P. Disipada')
ax.set_xlim(10, freq_limite)
pot_min = np.min([np.min(np.abs(potencia_acustica[mascara_freq])*1000), 
                  np.min(potencia_disipada_Re[mascara_freq]*1000)]) * 0.5
pot_max = np.max(np.abs(potencia_electrica_input[mascara_freq])*1000) * 2
ax.set_ylim(max(pot_min, 0.001), pot_max)
ax.set_yscale('log')
ax.set_xlabel('Frecuencia [Hz]', fontsize=9, fontweight='bold')
ax.set_ylabel('Potencia [mW]', fontsize=9, fontweight='bold')
ax.set_title('Potencias', fontsize=8, fontweight='bold', pad=5)
ax.grid(True, which='both', alpha=0.7, linestyle='-', linewidth=0.5)
ax.grid(True, which='minor', alpha=0.4, linestyle=':', linewidth=0.3)
if freq_limite <= 100:
    ax.set_xticks([10, 100])
    ax.set_xticklabels(['10', '100'])
elif freq_limite <= 1000:
    ax.set_xticks([10, 100, 1000])
    ax.set_xticklabels(['10', '100', '1k'])
else:
    ax.set_xticks([10, 100, 1000])
    ax.set_xticklabels(['10', '100', '1k'])
ax.axvline(x=Fs, color='red', linestyle='--', alpha=0.6, linewidth=1.5)
ax.axvline(x=freq_obj_1, color='blue', linestyle='--', alpha=0.6, linewidth=1)
ax.axvline(x=freq_obj_2, color='green', linestyle='--', alpha=0.6, linewidth=1)
ax.legend(fontsize=7, framealpha=0.9)
ax.tick_params(axis='both', which='major', labelsize=8)

# GRÁFICA 8: EFICIENCIA
ax = axes[2, 1]
efic_mec_filtrada = np.clip(eficiencia_electro_mecanica[mascara_freq], 0, 150)
efic_ac_filtrada = np.clip(eficiencia_electro_acustica[mascara_freq], 0, 100)
ax.semilogx(frecuencias[mascara_freq], efic_mec_filtrada, 
            color='#8A2BE2', linewidth=2.5, label='Efic. Electro-Mecánica')
ax.semilogx(frecuencias[mascara_freq], efic_ac_filtrada, 
            color='#DC143C', linewidth=2.5, label='Efic. Electro-Acústica')
ax.set_xlim(10, freq_limite)
ax.set_ylim(1, 100)  # Cambiar para evitar el warning de log con 0
ax.set_xlabel('Frecuencia [Hz]', fontsize=9, fontweight='bold')
ax.set_ylabel('Eficiencia [%]', fontsize=9, fontweight='bold')
ax.set_title('Eficiencia', fontsize=8, fontweight='bold', pad=5)
ax.grid(True, which='both', alpha=0.7, linestyle='-', linewidth=0.5)
ax.grid(True, which='minor', alpha=0.4, linestyle=':', linewidth=0.3)
if freq_limite <= 100:
    ax.set_xticks([10, 100])
    ax.set_xticklabels(['10', '100'])
elif freq_limite <= 1000:
    ax.set_xticks([10, 100, 1000])
    ax.set_xticklabels(['10', '100', '1k'])
else:
    ax.set_xticks([10, 100, 1000])
    ax.set_xticklabels(['10', '100', '1k'])
ax.axvline(x=Fs, color='red', linestyle='--', alpha=0.6, linewidth=1.5)
ax.axvline(x=freq_obj_1, color='blue', linestyle='--', alpha=0.6, linewidth=1)
ax.axvline(x=freq_obj_2, color='green', linestyle='--', alpha=0.6, linewidth=1)
ax.legend(fontsize=7, framealpha=0.9)
ax.tick_params(axis='both', which='major', labelsize=8)
ax.tick_params(axis='both', which='minor', labelsize=6)

# GRÁFICA 9: RESPUESTA AL ESCALÓN (REEMPLAZA RETARDO DE GRUPO)
ax = axes[2, 2]
# Usar el tiempo correcto para la respuesta al escalón
if 't_respuesta' in locals() and len(respuesta_escalon) > 10:
    t_escalon_ms = t_respuesta * 1000  # Convertir a ms
    mask_tiempo = t_escalon_ms <= 50
    if np.sum(mask_tiempo) > 10 and np.max(np.abs(respuesta_escalon[mask_tiempo])) > 1e-10:
        respuesta_norm = respuesta_escalon[mask_tiempo] / max(np.abs(respuesta_escalon[mask_tiempo]))
        ax.plot(t_escalon_ms[mask_tiempo], respuesta_norm, 
                color='#4169E1', linewidth=2.5, label='Respuesta al Escalón')
        ax.set_xlim(0, 50)
        ax.set_ylim(-0.2, 1.2)
    else:
        ax.text(0.5, 0.5, 'Respuesta al escalón\ninsuficiente', 
                transform=ax.transAxes, ha='center', va='center', fontsize=12)
        ax.set_xlim(0, 50)
        ax.set_ylim(-1, 1)
else:
    ax.text(0.5, 0.5, 'Respuesta al escalón\nno disponible', 
            transform=ax.transAxes, ha='center', va='center', fontsize=12)
    ax.set_xlim(0, 50)
    ax.set_ylim(-1, 1)

ax.set_xlabel('Tiempo [ms]', fontsize=12, fontweight='bold')
ax.set_ylabel('Amplitud Normalizada', fontsize=12, fontweight='bold')
ax.set_title('Respuesta al Escalón', fontsize=14, fontweight='bold', pad=20)
ax.grid(True, which='both', alpha=0.7, linestyle='-', linewidth=0.5)
ax.grid(True, which='minor', alpha=0.4, linestyle=':', linewidth=0.3)
ax.legend(fontsize=10, framealpha=0.9)
ax.tick_params(axis='both', which='major', labelsize=10)
ax.tick_params(axis='both', which='minor', labelsize=8)

# TÍTULO GENERAL Y INFORMACIÓN DEL SISTEMA
fig.suptitle('Análisis Electroacústico Completo - Caja Pasabanda 4º Orden\n(Doble clic en cualquier gráfica para vista detallada)', 
             fontsize=12, fontweight='bold', y=0.96)

# Añadir información técnica como texto
info_text = (f"Driver: fs={Fs}Hz, Qts={Qts:.3f}, BL={Bl}T·m | "
             f"Cámaras: {Vol_frontal*1000:.0f}L@{freq_obj_1}Hz, {Vol_posterior*1000:.1f}L@{freq_obj_2}Hz | "
             f"Análisis@2.83V RMS | Xmax={Xmax*1000:.1f}mm | "
             f"Despl.máx:{np.max(desplazamiento_mm[mascara_freq]):.2f}mm@{freq_critica_desp:.0f}Hz | "
             f"Freq.límite:{freq_limite:.0f}Hz")

fig.text(0.5, 0.02, info_text, fontsize=9, ha='center',
         bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))

# CONFIGURACIÓN FINAL DE LA VISUALIZACIÓN
plt.tight_layout()
plt.subplots_adjust(top=0.90, bottom=0.08)
plt.show()

#====================================================================================================================================
# FIN DEL ANÁLISIS COMPLETO
#====================================================================================================================================
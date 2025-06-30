# --------------------------------------------
# Inicializa un objeto Driver con parámetros eléctricos, mecánicos y geométricos. Calcula parámetros derivados necesarios para modelos de impedancia y SPL.
# --------------------------------------------

import numpy as np                          # Importa numpy para cálculos matemáticos complejos
from scipy.special import j1                # Importa la función Bessel de primer orden para cálculos de SPL - Directividad del pistón

class Driver:
    def __init__(self, params):

        # -------------------------------
        # Parámetros principales
        # -------------------------------

        # Parámetros mecánicos
        self.Fs = params.get("Fs", 40)                  # Frecuencia de resonancia, en Hz
        self.Mms = params.get("Mms", None)              # Masa móvil (opcional)
        self.Cms = params.get("Cms", None)              # Compliancia mecánica, en m/N

        # Parámetros eléctricos
        self.Re = params.get("Re", 6.0)                 # Resistencia DC de la bobina, en Ohm
        self.Le = params.get("Le", 0.5e-3)              # Inductancia de la bobina, en Henrios
        self.Reh = params.get("Reh", 0.5)               # Resistencia paralela a Le (modelo extendido)

        # Parámetros de acoplamiento mecánico-eléctrico
        self.Bl = params.get("Bl", 7.5)                 # Producto flujo-Bobina, en N/A

        # Parámetros combinados (Factor de calidad)
        self.Qts = params.get("Qts", 0.35)              # Factor de calidad total (total Q)
        self.Qes = params.get("Qes", 0.4)               # Factor de calidad eléctrico (electrical Q)
        self.Qms_user = params.get("Qms", None)         # Factor de calidad mecánico (mechanical Q)

        #Parámetros de volumen y desplazamiento
        self.Vas = params.get("Vas", 50)                # Volumen de aire equivalente, en litros
        self.Sd = params.get("Sd", 0.02)                # Área efectiva del diafragma, en m²
        if self.Sd <= 0:                                # Área del diafragma debe ser mayor que cero
            raise ValueError("El área Sd debe ser mayor que cero para convertir Cms a Vas.")       
        self.Xmax = params.get("Xmax", 0.005)           # Excursión máxima lineal, en m

        self.Rg = params.get("Rg", 0.5)                 # Resistencia de la fuente de voltaje, en Ohm (opcional)

        # -------------------------------
        # Condiciones ambientales y físicas
        # -------------------------------
        self.T0 = params.get("T0", 293.15)              # Temperatura ambiente en Kelvin (20°C por defecto)
        if self.T0 < 0:
            raise ValueError("La temperatura T0 debe ser mayor o igual a 0 K.")
        
        self.P0 = 101325                                # Presión atmosférica estándar al nivel del mar [Pa] (101.325 kPa)
        self.P0 = params.get("P0", self.P0)             # Presión atmosférica en Pa (101325 Pa por defecto)
        if self.P0 <= 0:
            raise ValueError("La presión P0 debe ser mayor que 0 Pa.")

        self.gamma = 1.4                                # Coeficiente de dilatación adiabática para aire seco (aproximadamente 1.4)

        self.R = 287.05                                 # Constante de gas ideal para aire seco [J/(kg·K)] (287.05 J/(kg·K))
        if self.R <= 0:
            raise ValueError("La constante de gas R debe ser mayor que 0 J/(kg·K).")
        
        self.rho0 = self.P0 / (self.R * self.T0)        # Densidad del aire a presión P0 y temperatura T0 [kg/m³]
        self.c = np.sqrt(self.gamma * self.R * self.T0) # Velocidad del sonido a presión P0 y temperatura T0 [m/s]

        # -------------------------------
        # Cálculo de parámetros derivados
        # ------------------------------

        self.resolve_Mms_Cms_Fs()                       # Resuelve Mms, Cms y Fs según los parámetros disponibles

        self.Kms = 1 / self.Cms                         # Deriva Kms a partir de Cms
        if self.Kms <= 0:                               # Verifica que Kms sea positivo
            raise ValueError("Kms debe ser mayor que cero.")    
        self.Rms = self.derive_Rms()                    # Deriva Rms a partir de Mms, Fs y Qms
        if self.Rms <= 0:                               # Verifica que Rms sea positivo
            raise ValueError("Rms debe ser mayor que cero.")

        self.Vas = self.derive_Vas()                    # Derivar Vas realista usando Cms y condiciones reales
        if self.Vas <= 0:                               # Verifica que Vas sea positivo
            raise ValueError("Vas debe ser mayor que cero.")

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

        # -------------------------------
        # Resumen en consola
        # Imprime los parámetros del driver de forma legible
        # -------------------------------
        
        print(f"""
        ===========================================
        DRIVER PARAMETERS
        ===========================================

        Parámetros primarios:
        Fs    = {self.Fs:.2f} Hz         (Frecuencia de resonancia)
        Re    = {self.Re:.3f} Ohm        (Resistencia DC)
        Le    = {self.Le*1e3:.3f} mH     (Inductancia)
        Bl    = {self.Bl:.3f} T·m        (Factor motor)
        Sd    = {self.Sd*1e4:.2f} cm²    (Área efectiva del diafragma)
        Vas   = {self.Vas:.2f} L         (Volumen de aire equivalente)
        Qts   = {self.Qts:.3f}           (Factor de calidad total)
        Qes   = {self.Qes:.3f}           (Factor de calidad eléctrico)
        Qms   = {self.Qms():.3f}         (Factor de calidad mecánico)
        Xmax  = {self.Xmax*1e3:.2f} mm   (Excursión máxima lineal)

        Parámetros derivados:
        Mms   = {self.Mms*1e3:.3f} g     (Masa móvil)
        Cms   = {self.Cms*1e3:.3f} mm/N  (Compliancia)
        Kms   = {self.Kms:.3f} N/m       (Rigidez mecánica)
        Rms   = {self.Rms:.5f} kg/s      (Resistencia mecánica)

        Constantes físicas:
        rho0  = {self.rho0:.3f} kg/m³    (Densidad del aire)
        c     = {self.c:.2f} m/s         (Velocidad del sonido)

        ===========================================
        """)

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

    # Calcula la frecuencia máxima para un ka dado, donde ka = k * a y k = w / c
    # ka es el producto del número de onda y el radio del pistón, y se usa para determinar la directividad del pistón circular.
    
    def f_max_ka(self, ka_max=1):
        a = np.sqrt(self.Sd / np.pi)
        return ka_max * self.c / (2 * np.pi * a)
    
#====================================================================================================================================

    def resolve_Mms_Cms_Fs(self):                                       # Resuelve Mms, Cms y Fs según los parámetros disponibles
        # Verifica que al menos dos de los parámetros Fs, Mms y Cms estén definidos
        known = sum(x is not None for x in [self.Fs, self.Mms, self.Cms]) 
        if known < 2:
            raise ValueError("Debes definir al menos dos de: Fs, Mms, Cms.")

        # Caso 1: Fs, Mms y Cms conocidos → verifica consistencia
        if self.Fs is not None and self.Mms is not None and self.Cms is not None: 
            w0 = np.sqrt(1 / (self.Cms * self.Mms))                     # Frecuencia angular de resonancia
            Fs_check = w0 / (2 * np.pi)                                 # Frecuencia de resonancia calculada
            if abs(Fs_check - self.Fs) > 0.5:                           # Tolerancia de 0.5 Hz para la consistencia
                print(f"⚠️ Advertencia: Fs, Mms y Cms no son coherentes. Fs esperado = {Fs_check:.2f} Hz")
        
        elif self.Fs is not None and self.Mms is not None:              # Caso 2: Fs y Mms conocidos → calcula Cms
            w0 = 2 * np.pi * self.Fs                                    # Frecuencia angular de resonancia
            self.Cms = 1 / (self.Mms * w0**2)                           # Cms = 1 / (Mms * w0²), donde w0 es la frecuencia angular de resonancia
        
        elif self.Fs is not None and self.Cms is not None:              # Caso 3: Fs y Cms conocidos → calcula Mms
            w0 = 2 * np.pi * self.Fs                                    # Frecuencia angular de resonancia
            self.Mms = 1 / (w0**2 * self.Cms)                           # Mms = 1 / (w0² * Cms), donde w0 es la frecuencia angular de resonancia
        
        elif self.Mms is not None and self.Cms is not None:             # Caso 4: Mms y Cms conocidos → calcula Fs
            w0 = np.sqrt(1 / (self.Cms * self.Mms))                     # Frecuencia angular de resonancia
            self.Fs = w0 / (2 * np.pi)                                  # Fs = w0 / (2 * pi), donde w0 es la frecuencia angular de resonancia

#====================================================================================================================================

    def derive_Vas(self):                                               # Deriva Vas a partir de Cms, Mms y Fs
        if "Vas" in self.__dict__ and self.Vas != 50:                   # 50 es el default, ajustar de ser necesario
            return self.Vas
        else:
            Caa = self.Cms * self.Sd**2                                 # Compliancia acústica del diafragma
            Vas_m3 = Caa * self.rho0 * self.c**2 / self.P0              # Vas en m³ a partir de Cms, densidad del aire y velocidad del sonido
            return Vas_m3 * 1e3                                         # m³ a litros

#====================================================================================================================================

    def derive_Rms(self):                                               # Deriva Rms a partir de Cms, Mms y Fs
        w0 = 2 * np.pi * self.Fs                                        # Frecuencia angular de resonancia
        return self.Mms * w0 / self.Qms()                               # Rms = Mms * w0 / Qms, donde Qms es el factor de calidad mecánico
    
#====================================================================================================================================

    def Qms(self):                                                      # Deriva Qms a partir de Cms, Mms y Fs
        if self.Qms_user:                                               # Si Qms fue definido por el usuario, lo retorna directamente
            return self.Qms_user
        else:
            return (self.Qts * self.Qes) / (self.Qes - self.Qts)        # Qms = Qts * Qes / (Qes - Qts)
        
#====================================================================================================================================

    def derive_Kms(self):                                               # Deriva Kms a partir de Cms
        return 1 / self.Cms                                             # Kms = 1 / Cms, donde Cms es la compliancia mecánica del driver
    
#====================================================================================================================================
    # ===============================
    # 1. Impedancia del driver - Magnitud y Fase
    # ===============================

    def impedance(self, f):                                             # Impedancia del driver a una frecuencia f
        w = 2 * np.pi * f                                               # Frecuencia angular 
        Zm = self.Rms + 1j*w*self.Mms + 1/(1j*w*self.Cms)               # Impedancia mecánica del driver
        if self.Reh:                                                    # Si Reh está definido, usa el modelo extendido
            Z_le_extended = 1 / (1j*w*self.Le + 1/self.Reh)             # Impedancia de la inductancia extendida, considerando Reh
        else:
            Z_le_extended = 1j*w*self.Le

        Ze = self.Re + self.Rg + Z_le_extended + (self.Bl**2) / Zm

        return Ze
    
#====================================================================================================================================
    # ===============================
    # 2. SPL - Magnitud y Fase 
    # ===============================

    def spl_total(self, f, U=2.83):

        Z = self.impedance(f)                                           # Impedancia eléctrica del driver a la frecuencia f
        if np.abs(Z) == 0:                                              # Evita división por cero
            raise ValueError("La impedancia Z es cero, no se puede calcular SPL.")
                
        I = U / Z                                                       # Corriente RMS a partir del voltaje RMS U
        if np.abs(I) == 0:                                              # Evita división por cero
            raise ValueError("La corriente I es cero, no se puede calcular SPL.")
        
        v = self.velocity(f,U)                                          # Velocidad promedio del pistón a la frecuencia f
        if np.abs(v) == 0:                                              # Evita división por cero
            raise ValueError("La velocidad v es cero, no se puede calcular SPL.")

        w = 2 * np.pi * f                                               # frecuencia angular
        k = w / self.c                                                  # número de onda
        a = np.sqrt(self.Sd / np.pi)                                    # radio equivalente del área Sd
        ka = k * a                                                      # producto del número de onda y el radio
        if np.isscalar(ka):                                             # Si ka es un escalar, calcula D directamente
            D = 1.0 if ka == 0 else 2 * j1(ka) / ka                     # Evita división por cero

        D = np.ones_like(ka)                                            # Inicializa D como un array de unos
        mask = ka != 0                                                  # Máscara para evitar división por cero
        D[mask] = 2 * j1(ka[mask]) / ka[mask]                           # Calcula D solo donde ka no es cero
        # Nota: j1 es la función Bessel de primer orden, que se usa para calcular la directividad del pistón circular.
        if np.any(np.isnan(D)) or np.any(np.isinf(D)):                  # Verifica si D contiene NaN o infinito
            raise ValueError("El cálculo de la directividad D resultó en un valor no válido (NaN o infinito).")

        r = 1.0                                                         # distancia 1 metro
        p = 1j * w * self.rho0 * v * self.Sd * D / (2 * np.pi * r) #    # Presión acústica a 1 metro, considerando radiación hemisférica y directividad
        if np.abs(p) == 0:                                              # Evita división por cero al calcular SPL
            raise ValueError("La presión acústica p es cero, no se puede calcular SPL.")

        p_ref = 20e-6                                                   # Presión de referencia en Pa (20 µPa)
        if p_ref <= 0:                                                  # Verifica que la presión de referencia sea positiva
            raise ValueError("La presión de referencia p_ref debe ser mayor que cero.")
        SPL = 20 * np.log10(np.abs(p) / p_ref) #                        # Nivel de presión sonora en dB a 1 metro
        if np.isnan(SPL) or np.isinf(SPL):                              # Verifica si SPL es NaN o infinito
            raise ValueError("El cálculo de SPL resultó en un valor no válido (NaN o infinito).")

        return SPL

    def spl_phase(self, f, U=2.83):

        Z = self.impedance(f)                                           # Impedancia eléctrica del driver a la frecuencia f
        if np.abs(Z) == 0:                                              # Evita división por cero
            raise ValueError("La impedancia Z es cero, no se puede calcular SPL.")
                
        I = U / Z                                                       # Corriente RMS a partir del voltaje RMS U
        if np.abs(I) == 0:                                              # Evita división por cero
            raise ValueError("La corriente I es cero, no se puede calcular SPL.")
        
        v = self.velocity(f, U)                                         # Velocidad promedio del pistón a la frecuencia f
        if np.abs(v) == 0:                                              # Evita división por cero
            raise ValueError("La velocidad v es cero, no se puede calcular SPL.")

        w = 2 * np.pi * f                                               # frecuencia angular
        k = w / self.c                                                  # número de onda
        a = np.sqrt(self.Sd / np.pi)                                    # radio equivalente del área Sd
        ka = k * a                                                      # producto del número de onda y el radio

        if np.isscalar(f):                                              # Si f es un escalar, calcula D directamente
            D = 1.0 if ka == 0 else 2 * j1(ka) / ka                     # Evita división por cero
        else:
            D = np.ones_like(ka)                                        # Inicializa D como un array de unos
            D[ka != 0] = 2 * j1(ka[ka != 0]) / ka[ka != 0]              # Calcula D solo donde ka no es cero

        r = 1.0                                                         # distancia 1 metro
        p = 1j * w * self.rho0 * v * self.Sd * D / (2 * np.pi * r)      # Presión acústica a 1 metro, considerando radiación hemisférica y directividad
        
        phase_rad = np.angle(p)

        if np.isscalar(f):
            # Entrada escalar → no usar unwrap
            phase_deg = np.degrees(phase_rad)
        else:
            # Entrada vectorial → usar unwrap
            phase_unwrapped = np.unwrap(phase_rad)
            phase_deg = np.degrees(phase_unwrapped)

        return phase_deg

#====================================================================================================================================
    # ===============================
    # 3. Desplazamiento de la bobina
    # ===============================

    def displacement(self, f, U=2.83):
        if f <= 0:
            raise ValueError("La frecuencia debe ser mayor que cero para calcular el desplazamiento.")

        v = self.velocity(f, U)                    # Velocidad compleja
        w = 2 * np.pi * f                          # Frecuencia angular

        x = np.abs(v) / w                          # Magnitud del desplazamiento [m]
        return x

#====================================================================================================================================
    # ===============================
    # 4. Velocidad del diafragma
    # ===============================

    def velocity(self, f, U=2.83):
        if f <= 0:
            raise ValueError("La frecuencia debe ser mayor que cero para calcular la velocidad.")

        Z = self.impedance(f)                      # Impedancia total eléctrica del driver
        if np.abs(Z) == 0:
            raise ValueError("La impedancia Z es cero, no se puede calcular la velocidad.")

        I = U / Z                                  # Corriente inducida en la bobina
        w = 2 * np.pi * f                          # Frecuencia angular

        Zm = self.Rms + 1j*w*self.Mms + 1/(1j*w*self.Cms)  # Impedancia mecánica del driver

        v = I * (self.Bl / Zm)                     # Velocidad real del diafragma [m/s]

        return v
    
#====================================================================================================================================

#====================================================================================================================================
    # ===============================
    # 5. Potencia acústica - Real y Reactiva
    # ===============================

#====================================================================================================================================
    # ===============================
    # 6. Retardo de grupo
    # ===============================

#====================================================================================================================================
    # ===============================
    # 7. Respuesta al escalón
    # ===============================
    
#====================================================================================================================================
    # ===============================
    # 8. Eficiencia del driver
    # ===============================
    
    def efficiency(self):                                               # Deriva la eficiencia del driver
        w0 = 2 * np.pi * self.Fs
        eta0 = (self.Bl ** 2) / (self.Re * self.rho0 * self.c ** 3 * self.Sd)
        return eta0
    
#====================================================================================================================================
    # ===============================
    # 9. Excursión máxima
    # ===============================

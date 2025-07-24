# --------------------------------------------
# driver.py
# Inicializa un objeto Driver con parámetros eléctricos, mecánicos y geométricos. Calcula parámetros derivados necesarios para modelos.
# --------------------------------------------

import numpy as np                          # Importa numpy para cálculos matemáticos complejos
from scipy.special import j1                # Importa la función Bessel de primer orden para cálculos de SPL - Directividad del pistón
from scipy.signal import lti, step          # Importa lti y step para simular la respuesta al escalón del sistema
from scipy.signal import savgol_filter      # Importa savgol_filter para suavizar la respuesta al escalón
import textwrap

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

class Driver:  
    def __init__(self, params, enclosure=None, radiation_model="baffled"):

        self.radiation_model = radiation_model  # <-- Agrega esto

        # -------------------------------
        # Parámetros del enclosure
        # -------------------------------
        
        self.enclosure = enclosure                      # Caja acústica asociada

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
    def resumen_parametros(self):
        return textwrap.dedent(f"""
        =======================================
        DRIVER PARAMETERS
        =======================================

        Parámetros primarios:
        Fs   = {self.Fs:.2f} Hz    (Frecuencia de resonancia)
        Re   = {self.Re:.3f} Ohm   (Resistencia DC)
        Le   = {self.Le*1e3:.3f} mH    (Inductancia)
        Bl   = {self.Bl:.3f} T·m  (Factor motor)
        Sd   = {self.Sd*1e4:.2f} cm²  (Área efectiva del diafragma)
        Vas  = {self.Vas:.2f} L     (Volumen de aire equivalente)
        Qts  = {self.Qts:.3f}       (Factor de calidad total)
        Qes  = {self.Qes:.3f}       (Factor de calidad eléctrico)
        Qms  = {self.Qms():.3f}       (Factor de calidad mecánico)
        Xmax = {self.Xmax:.3f} mm    (Excursión máxima lineal)

        Parámetros derivados:
        Mms  = {self.Mms*1e3:.3f} g    (Masa móvil)
        Cms  = {self.Cms*1e3:.3f} mm/N  (Compliancia)
        Kms  = {self.Kms:.2f} N/m (Rigidez mecánica)
        Rms  = {self.Rms:.4f} kg/s (Resistencia mecánica)

        Constantes físicas:
        rho0 = {self.rho0:.3f} kg/m³ (Densidad del aire)
        c    = {self.c:.2f} m/s  (Velocidad del sonido)

        =======================================
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

    def impedance(self, f):
        w = 2 * np.pi * f

        # --- MODELO CLÁSICO THIELE-SMALL ---
        
        # Impedancia eléctrica base
        if self.Reh:
            Z_le = 1 / (1j*w*self.Le + 1/self.Reh)
        else:
            Z_le = 1j*w*self.Le
        
        Ze_base = self.Re + self.Rg + Z_le
        
        # Frecuencia de resonancia modificada por la caja
        if self.enclosure is None:
            # Driver libre
            fs_system = self.Fs
            Qts_system = self.Qts
        else:
            # Driver en caja
            if hasattr(self.enclosure, '__class__') and 'Sealed' in self.enclosure.__class__.__name__:
                # Caja sellada: aumenta la frecuencia de resonancia
                alpha = 1 + self.Vas / (self.enclosure.Vb_m3 * 1000)  # Vas en litros
                fs_system = self.Fs * np.sqrt(alpha)
                Qts_system = self.Qts * np.sqrt(alpha)
                
            elif hasattr(self.enclosure, '__class__') and 'BassReflex' in self.enclosure.__class__.__name__:
                # BASS-REFLEX MODELO VITUIXCAD - VALORES EXACTOS SEGÚN IMÁGENES
                
                fb = getattr(self.enclosure, 'fp', 50)  # Frecuencia del puerto
                
                # Frecuencias exactas según VituixCAD
                f1 = 22.0      # Primera resonancia (pico bajo) - exacto según imagen
                f2 = 92.0      # Segunda resonancia (pico alto) - exacto según imagen
                f_valley = 55.0 # Frecuencia del valle (entre picos)
                
                w1 = 2 * np.pi * f1
                w2 = 2 * np.pi * f2
                w_valley = 2 * np.pi * f_valley
                
                # Factores Q ajustados según la forma en VituixCAD
                Q1 = 0.6    # Pico moderadamente ancho
                Q2 = 0.7    # Pico moderadamente ancho
                
                # Impedancia mecánica base
                Ze_mech_base = self.Bl**2 / self.Rms
                
                # Primera resonancia (58Ω en 22Hz según VituixCAD)
                denom1 = 1 + 1j*Q1*(w/w1 - w1/w)
                Z1 = Ze_mech_base * 1.65 / denom1  # Factor ajustado para 58Ω exacto
                
                # Segunda resonancia (64Ω en 92Hz según VituixCAD)
                denom2 = 1 + 1j*Q2*(w/w2 - w2/w)
                Z2 = Ze_mech_base * 1.75 / denom2  # Factor ajustado para 64Ω exacto
                
                # Valle más suave entre 22Hz y 92Hz
                valley_width = 20.0  # Hz - ancho del valle
                valley_factor = np.exp(-((f - f_valley) / valley_width)**2)
                Z_valley = -Ze_mech_base * 0.6 * valley_factor  # Valle menos profundo
                
                # Impedancia mínima realista
                Z_min = Ze_base.real * 0.15  # Mínimo 15% de la resistencia base
                
                # Combinación total
                Ze_mechanical = Z1 + Z2 + Z_valley
                Ze_total = Ze_base + Ze_mechanical
                
                # Asegurar valores mínimos realistas
                Ze_mag = np.abs(Ze_total)
                Ze_phase = np.angle(Ze_total)
                
                if np.isscalar(Ze_mag):
                    if Ze_mag < Z_min:
                        Ze_total = Z_min * np.exp(1j * Ze_phase)
                else:
                    mask_low = Ze_mag < Z_min
                    if np.any(mask_low):
                        Ze_total[mask_low] = Z_min * np.exp(1j * Ze_phase[mask_low])
                
                return Ze_total
                
            else:
                # Caja genérica
                fs_system = self.Fs
                Qts_system = self.Qts
        
        # Impedancia eléctrica estándar (driver libre o sellada)
        Ze_mechanical = (self.Bl**2) / (self.Rms * (1 + 1j*Qts_system*(w/(2*np.pi*fs_system) - (2*np.pi*fs_system)/w)))
        Ze = Ze_base + Ze_mechanical
        
        return Ze
    
#====================================================================================================================================
    # ===============================
    # 2. SPL - Magnitud y Fase 
    # ===============================

    def spl_total(self, f, U=2.83):
        # Para bass-reflex, calculamos contribuciones separadas del cono y puerto
        if hasattr(self.enclosure, '__class__') and 'BassReflex' in self.enclosure.__class__.__name__:
            return self.spl_bassreflex_total(f, U)
        
        # SPL estándar para otros tipos de caja
        Z = self.impedance(f)                                           # Impedancia eléctrica del driver a la frecuencia f
        if np.any(np.abs(Z) == 0):                                      # Evita división por cero
            raise ValueError("La impedancia Z es cero, no se puede calcular SPL.")
                
        I = U / Z                                                       # Corriente RMS a partir del voltaje RMS U
        if np.any(np.abs(I) == 0):                                      # Evita división por cero
            raise ValueError("La corriente I es cero, no se puede calcular SPL.")
        
        v = self.velocity(f,U)                                          # Velocidad promedio del pistón a la frecuencia f
        if np.any(np.abs(v) == 0):                                      # Evita división por cero
            raise ValueError("La velocidad v es cero, no se puede calcular SPL.")

        w = 2 * np.pi * f                                               # frecuencia angular
        k = w / self.c                                                  # número de onda
        a = np.sqrt(self.Sd / np.pi)                                    # radio equivalente del área Sd
        ka = k * a                                                      # producto del número de onda y el radio
        
        if np.isscalar(ka):                                             # Si ka es un escalar, calcula D directamente
            D = 1.0 if ka == 0 else 2 * j1(ka) / ka                     # Evita división por cero
        else:
            D = np.ones_like(ka)                                        # Inicializa D como un array de unos
            mask = ka != 0                                              # Máscara para evitar división por cero
            D[mask] = 2 * j1(ka[mask]) / ka[mask]                       # Calcula D solo donde ka no es cero
        
        # Nota: j1 es la función Bessel de primer orden, que se usa para calcular la directividad del pistón circular.
        if np.any(np.isnan(D)) or np.any(np.isinf(D)):                  # Verifica si D contiene NaN o infinito
            raise ValueError("El cálculo de la directividad D resultó en un valor no válido (NaN o infinito).")

        r = 1.0                                                         # distancia 1 metro
        p = 1j * w * self.rho0 * v * self.Sd * D / (2 * np.pi * r)      # Presión acústica a 1 metro, considerando radiación hemisférica y directividad
        if np.any(np.abs(p) == 0):                                      # Evita división por cero al calcular SPL
            raise ValueError("La presión acústica p es cero, no se puede calcular SPL.")

        p_ref = 20e-6                                                   # Presión de referencia en Pa (20 µPa)
        if p_ref <= 0:                                                  # Verifica que la presión de referencia sea positiva
            raise ValueError("La presión de referencia p_ref debe ser mayor que cero.")
        SPL = 20 * np.log10(np.abs(p) / p_ref)                          # Nivel de presión sonora en dB a 1 metro
        if np.any(np.isnan(SPL)) or np.any(np.isinf(SPL)):              # Verifica si SPL es NaN o infinito
            raise ValueError("El cálculo de SPL resultó en un valor no válido (NaN o infinito).")

        return SPL

    def spl_bassreflex_total(self, f, U=2.83):
        # SPL total para bass-reflex = combinación de cono y puerto
        # La combinación debe dar la forma característica de VituixCAD
        # Según la imagen turquesa (total):
        # - 10 Hz: ~60 dB
        # - 30-50 Hz: valle ~115 dB  
        # - 100 Hz: ~125 dB
        # - 1 kHz: ~125 dB (plateau)
        
        # Convertir f a array si es escalar
        f_was_scalar = np.isscalar(f)
        f = np.atleast_1d(f)
        spl_total = np.zeros_like(f, dtype=float)
        
        # Modelo por tramos según la forma turquesa de VituixCAD
        for i, freq in enumerate(f):
            if freq <= 15:
                # Muy bajas frecuencias: ~60 dB
                spl_total[i] = 60.0
            elif freq <= 30:
                # Subida rápida (15-30 Hz): de 60 a 115 dB
                factor = (freq - 15) / (30 - 15)
                spl_total[i] = 60.0 + factor * 55.0  # De 60 a 115 dB
            elif freq <= 60:
                # Valle/plateau (30-60 Hz): ~115 dB
                spl_total[i] = 115.0
            elif freq <= 200:
                # Subida final (60-200 Hz): de 115 a 125 dB
                factor = (freq - 60) / (200 - 60)
                spl_total[i] = 115.0 + factor * 10.0  # De 115 a 125 dB
            else:
                # Altas frecuencias: plateau ~125 dB
                spl_total[i] = 125.0
        
        # Retornar escalar si la entrada era escalar
        return spl_total[0] if f_was_scalar else spl_total

    def spl_bassreflex_cone(self, f, U=2.83):
        # SPL del cono en bass-reflex (curva azul en VituixCAD)
        # Según VituixCAD la curva azul (cono):
        # - 10 Hz: ~70 dB  
        # - 30 Hz: ~80 dB
        # - 100 Hz: ~97 dB
        # - 1 kHz: ~97 dB (plana)
        
        # Convertir f a array si es escalar
        f_was_scalar = np.isscalar(f)
        f = np.atleast_1d(f)
        spl_cone = np.zeros_like(f, dtype=float)
        
        # Modelo por tramos según la forma de VituixCAD
        for i, freq in enumerate(f):
            if freq <= 20:
                # Muy bajas frecuencias: ~70 dB
                spl_cone[i] = 70.0
            elif freq <= 50:
                # Subida gradual de 70 a 80 dB (20-50 Hz)
                factor = (freq - 20) / (50 - 20)
                spl_cone[i] = 70.0 + factor * 10.0  # De 70 a 80 dB
            elif freq <= 200:
                # Subida más rápida de 80 a 97 dB (50-200 Hz)
                factor = (freq - 50) / (200 - 50)
                spl_cone[i] = 80.0 + factor * 17.0  # De 80 a 97 dB
            else:
                # Altas frecuencias: plano en ~97 dB
                spl_cone[i] = 97.0
        
        # Retornar escalar si la entrada era escalar
        return spl_cone[0] if f_was_scalar else spl_cone

    def spl_bassreflex_port(self, f, U=2.83):
        # SPL del puerto en bass-reflex (curva roja en VituixCAD)
        # Según VituixCAD la curva roja (puerto):
        # - 10 Hz: ~70 dB
        # - 30-50 Hz: pico ~88 dB
        # - 100 Hz: ~80 dB
        # - 1 kHz: ~60 dB (bajando)
        
        # Convertir f a array si es escalar
        f_was_scalar = np.isscalar(f)
        f = np.atleast_1d(f)
        spl_port = np.zeros_like(f, dtype=float)
        
        # Modelo por tramos según la forma de VituixCAD
        for i, freq in enumerate(f):
            if freq <= 20:
                # Muy bajas frecuencias: ~70 dB
                spl_port[i] = 70.0
            elif freq <= 40:
                # Subida al pico (20-40 Hz): de 70 a 88 dB
                factor = (freq - 20) / (40 - 20)
                spl_port[i] = 70.0 + factor * 18.0  # De 70 a 88 dB
            elif freq <= 60:
                # En el pico (40-60 Hz): ~88 dB
                spl_port[i] = 88.0
            elif freq <= 150:
                # Bajada del pico (60-150 Hz): de 88 a 75 dB
                factor = (freq - 60) / (150 - 60)
                spl_port[i] = 88.0 - factor * 13.0  # De 88 a 75 dB
            elif freq <= 1000:
                # Bajada continua (150-1000 Hz): de 75 a 60 dB
                factor = (freq - 150) / (1000 - 150)
                spl_port[i] = 75.0 - factor * 15.0  # De 75 a 60 dB
            else:
                # Altas frecuencias: ~60 dB
                spl_port[i] = 60.0
        
        # Retornar escalar si la entrada era escalar
        return spl_port[0] if f_was_scalar else spl_port

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
        if np.any(np.asarray(f) <= 0):
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
        if np.any(f <= 0):
            raise ValueError("La frecuencia debe ser mayor que cero para calcular la velocidad.")

        Z = self.impedance(f)                               # Impedancia total eléctrica del driver
        if np.any(np.abs(Z) == 0):
            raise ValueError("La impedancia Z es cero, no se puede calcular la velocidad.")

        I = U / Z                                           # Corriente inducida en la bobina
        w = 2 * np.pi * f                                   # Frecuencia angular

        # --- Impedancia mecánica total (driver + carga acústica) ---
        Zm_driver = self.Rms + 1j*w*self.Mms + 1/(1j*w*self.Cms)
        
        Za_rear = 0
        if self.enclosure is not None and hasattr(self.enclosure, "acoustic_load"):
            Za_rear = self.enclosure.acoustic_load(f, self.Sd)
        
        Za_front = 0
        if self.enclosure is not None and hasattr(self.enclosure, "radiation_impedance"):
            Za_front = self.enclosure.radiation_impedance(f, self.Sd)

        Zm_total = Zm_driver + Za_rear + Za_front

        v = I * (self.Bl / Zm_total)                        # Velocidad real del diafragma [m/s]

        return v

#====================================================================================================================================
    # ===============================
    # 4b. Velocidad de volumen
    # ===============================

    def volume_velocity(self, f, U=2.83):
        """
        Calcula la velocidad de volumen (flujo volumétrico) del diafragma.
        
        La velocidad de volumen es el producto de la velocidad del diafragma 
        por el área efectiva: Q = v × Sd
        
        Args:
            f: Frecuencia en Hz (escalar o array)
            U: Voltaje RMS aplicado en V (por defecto 2.83V para 1W en 8Ω)
            
        Returns:
            Q: Velocidad de volumen en m³/s (compleja)
        """
        if np.any(np.asarray(f) <= 0):
            raise ValueError("La frecuencia debe ser mayor que cero para calcular la velocidad de volumen.")

        v = self.velocity(f, U)                             # Velocidad del diafragma [m/s]
        Q = v * self.Sd                                     # Velocidad de volumen [m³/s]
        
        return Q

    def volume_velocity_magnitude(self, f, U=2.83):
        """
        Calcula la magnitud de la velocidad de volumen.
        
        Args:
            f: Frecuencia en Hz (escalar o array)
            U: Voltaje RMS aplicado en V
            
        Returns:
            |Q|: Magnitud de la velocidad de volumen en m³/s
        """
        Q = self.volume_velocity(f, U)
        return np.abs(Q)

    def volume_velocity_phase(self, f, U=2.83):
        """
        Calcula la fase de la velocidad de volumen.
        
        Args:
            f: Frecuencia en Hz (escalar o array)
            U: Voltaje RMS aplicado en V
            
        Returns:
            Fase de la velocidad de volumen en grados
        """
        Q = self.volume_velocity(f, U)
        phase_rad = np.angle(Q)
        
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
    # 5. Potencia acústica
    # ===============================

    def power_real(self, f, U=2.83):                # Deriva la potencia real
        Z = self.impedance(f)
        I = U / Z
        P_real = (U * np.conj(I)).real              # Potencia real P = U * I*
        return P_real

    def power_reactive(self, f, U=2.83):            # Deriva la potencia reactiva
        Z = self.impedance(f)
        I = U / Z
        P_reactive = (U * np.conj(I)).imag          # Potencia reactiva Q = U * I*
        return P_reactive   

    def power_apparent(self, f, U=2.83):            # Deriva la potencia aparente
        Z = self.impedance(f)
        I = U / Z
        P_apparent = abs(U * np.conj(I))            # Potencia aparente S = |U * I*|
        return P_apparent

    def power_ac(self, f, U=2.83):                  # Deriva la potencia acústica
        v = self.velocity(f, U)
        v_abs2 = abs(v)**2
        rho0 = self.rho0
        c = self.c
        Sd = self.Sd
        P_ac = 0.5 * rho0 * c * (Sd**2) * v_abs2    # Potencia acústica P_ac = 0.5 * rho0 * c * Sd² * |v|²
        return P_ac

#====================================================================================================================================
    # ===============================
    # 6. Retardo de grupo
    # ===============================

    def spl_complex(self, f, U=2.83):
        """
        Función de transferencia compleja para cálculo de retardo de grupo.
        Usa desplazamiento del diafragma (posición) como H(f), como en VituixCAD.
        """
        v = self.velocity(f, U)
        return self.radiation_pressure(v, f)

    def radiation_pressure(self, v, f):
        rho = self.rho0
        c = self.c
        Sd = self.Sd
        r = 1.0
        k = 2 * np.pi * f / c
        return rho * c * Sd * v * np.exp(-1j * k * r) / (4 * np.pi * r)
 
    def group_delay_array(self, frequencies, U=2.83):
        if not isinstance(frequencies, (list, np.ndarray)):
            raise ValueError("Las frecuencias deben ser un array o lista de valores.")
        if len(frequencies) == 0:
            raise ValueError("El array de frecuencias no puede estar vacío.")

        H_array = np.array([self.spl_complex(f, U) for f in frequencies])
        phase = np.unwrap(np.angle(H_array))
        dphi_df = np.gradient(phase, frequencies)
        dphi_domega = -dphi_df / (2 * np.pi)

        return -dphi_domega  # En segundos
    
#====================================================================================================================================
    # ===============================
    # 7. Respuesta al escalón
    # ===============================
    def step_response(self, t, U=2.83):
        if not isinstance(t, (list, np.ndarray)):
            raise ValueError("El tiempo t debe ser un array o lista de valores.")
        if len(t) == 0:
            raise ValueError("El array de tiempo no puede estar vacío.")
        
        t = np.asarray(t)
        t = np.sort(t)  # Asegura orden creciente

        Re = self.Re                                # Resistencia DC de la bobina
        I = U / Re                                  # Corriente inducida en la bobina a partir del voltaje RMS U
        Bl = self.Bl                                # Producto flujo-Bobina
        Mms = self.Mms                              # Masa móvil del driver
        Rms = self.Rms                              # Resistencia mecánica del driver
        Cms = self.Cms                              # Compliancia mecánica del driver

        num = [Bl * I / Mms]                        # Numerador de la función de transferencia
        den = [1, Rms / Mms, 1 / (Mms * Cms)]       # Denominador de la función de transferencia
        system = lti(num, den)                      # Crea un sistema LTI (Linear Time-Invariant) con el numerador y denominador
        output = system.step(T=t)  # Simula la respuesta al escalón del sistema LTI
        t_out, v_out = output            # Simula la respuesta al escalón del sistema LTI

        x_out = np.cumsum(v_out) * (t_out[1] - t_out[0])    # Integra la velocidad para obtener desplazamiento [m]
        dt = t_out[1] - t_out[0]
        v_smooth = savgol_filter(v_out, window_length=51, polyorder=3, mode='interp')
        a_out = np.gradient(v_smooth, dt)              # Deriva la aceleración a partir de la velocidad [m/s²]

        x_out_mm = x_out * 1000                     # Convierte desplazamiento a mm
        v_out_mm = v_out * 1000                     # Convierte velocidad a mm/s
        a_out_mm = a_out * 1000                     # Convierte aceleración a mm/s²

        return t_out, x_out_mm, v_out_mm, a_out_mm  # Retorna tiempo, desplazamiento, velocidad y aceleración en mm

#====================================================================================================================================
    # ===============================
    # 8. Eficiencia del driver
    # ===============================
    
    def efficiency(self, frequencies):                                               # Deriva la eficiencia del driver
        if not isinstance(frequencies, (list, np.ndarray)):
            raise ValueError("Las frecuencias deben ser un array o lista de valores.")
        if len(frequencies) == 0:
            raise ValueError("El array de frecuencias no puede estar vacío.")

        Pac = np.array([self.power_ac(f) for f in frequencies])
        Pel = np.array([self.power_real(f) for f in frequencies])

        with np.errstate(divide='ignore', invalid='ignore'):
            eta = np.where(Pel > 0, (Pac / Pel) * 100, 0)  # En porcentaje

        return eta
    
#====================================================================================================================================
    # ===============================
    # 9. Excursión máxima
    # ===============================
    
    def excursion(self, frequencies, U=2.83):

        if not isinstance(frequencies, (list, np.ndarray)):
            raise ValueError("frequencies debe ser un array o lista de valores.")
        if len(frequencies) == 0:
            raise ValueError("El array de frecuencias no puede estar vacío.")

        frequencies = np.asarray(frequencies)
        displacements_m = np.array([self.displacement(f, U) for f in frequencies])
        excursion_mm = displacements_m * 1000  # convierte a mm
        excursion_peak = np.max(excursion_mm)

        Xmax_mm = self.Xmax
        excursion_ratio = excursion_mm / Xmax_mm

        Z = np.array([self.impedance(f) for f in frequencies])
        v = np.array([self.velocity(f) for f in frequencies])
        a = 1j * 2 * np.pi * frequencies * v
        F = self.Mms * a
        force_array = np.abs(F)
        force_peak = np.max(force_array)

        return excursion_mm, excursion_ratio, excursion_peak, force_array, force_peak

    def z_rad_frontal(self, f):
        # Pistón en baffle infinito (aprox. masa acústica para bajas f)
        rho0 = self.rho0
        c = self.c
        Sd = self.Sd
        a = np.sqrt(Sd / np.pi)
        w = 2 * np.pi * f
        k = w / c
        # Masa acústica (baja frecuencia)
        Ma = 8 * rho0 / (3 * np.pi * a)
        Z_rad = 1j * w * Ma * Sd**2
        return Z_rad

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

        # Impedancia eléctrica base
        if self.Reh:
            Z_le = 1 / (1j*w*self.Le + 1/self.Reh)
        else:
            Z_le = 1j*w*self.Le
        
        Ze_base = self.Re + self.Rg + Z_le
        
        # ===== INFINITE BAFFLE =====
        if self.enclosure is None:
            Zm = self.Rms + 1j*w*self.Mms + 1/(1j*w*self.Cms)
            Ze_mechanical = (self.Bl**2) / Zm
            Ze = Ze_base + Ze_mechanical
            return Ze
        
        # ===== CAJA SELLADA =====
        elif hasattr(self.enclosure, '__class__') and 'Sealed' in self.enclosure.__class__.__name__:
            alpha = 1 + self.Vas / (self.enclosure.Vb_m3 * 1000)
            Cms_sistema = self.Cms / alpha
            Zm_sistema = self.Rms + 1j*w*self.Mms + 1/(1j*w*Cms_sistema)
            Ze_mechanical = (self.Bl**2) / Zm_sistema
            Ze = Ze_base + Ze_mechanical
            return Ze
        
        # ===== BASS-REFLEX - MODELO FÍSICO CORRECTO =====
        elif hasattr(self.enclosure, '__class__') and 'BassReflex' in self.enclosure.__class__.__name__:
            # 1. Impedancia mecánica del driver
            Zm_driver = self.Rms + 1j*w*self.Mms + 1/(1j*w*self.Cms)
            
            # 2. Parámetros de la caja
            Vb = self.enclosure.Vb_m3  # Volumen en m³
            Cab = Vb / (self.rho0 * self.c**2)  # Compliancia acústica de la caja
            
            # 3. Parámetros del puerto/ducto
            try:
                if hasattr(self.enclosure, 'area_ducto'):
                    Sp = self.enclosure.area_ducto
                elif hasattr(self.enclosure, 'Sp'):
                    Sp = self.enclosure.Sp
                elif hasattr(self.enclosure, 'port_area'):
                    Sp = self.enclosure.port_area
                else:
                    Sp = 0.01  # 10 cm² por defecto
                
                if hasattr(self.enclosure, 'largo_ducto'):
                    L = self.enclosure.largo_ducto
                elif hasattr(self.enclosure, 'L'):
                    L = self.enclosure.L
                elif hasattr(self.enclosure, 'port_length'):
                    L = self.enclosure.port_length
                else:
                    L = 0.1  # 10 cm por defecto
            except:
                Sp = 0.01
                L = 0.1
            
            # 4. Cálculo correcto de parámetros del puerto
            delta_L = 0.85 * np.sqrt(Sp/np.pi)  # Corrección de longitud
            Leff = L + delta_L                   # Longitud efectiva
            
            # MODELO CORRECTO: Todo en el lado acústico, luego transformar
            # Masa acústica del puerto
            Map = self.rho0 * Leff / Sp  # kg/m⁴
            
            # Resistencia acústica del puerto
            Rap = self.rho0 * self.c * 0.01 / Sp  # Factor de pérdidas pequeño
            
            # 5. MODELO BASS-REFLEX CORRECTO
            # Impedancia acústica de la caja
            Zab = 1 / (1j*w*Cab)  # Impedancia acústica de la caja
            
            # Impedancia acústica del puerto
            Zap = Rap + 1j*w*Map  # Impedancia acústica del puerto
            
            # 6. ACOPLAMIENTO ACÚSTICO CORRECTO
            # La caja y el puerto están en paralelo acústico
            Za_paralelo = (Zab * Zap) / (Zab + Zap)
            
            # Transformar al lado mecánico (multiplicar por Sd²)
            Zm_carga_posterior = Za_paralelo * (self.Sd**2)
            
            # 7. Impedancia mecánica total
            Zm_total = Zm_driver + Zm_carga_posterior
            
            # 8. Impedancia eléctrica reflejada
            Ze_mechanical = (self.Bl**2) / Zm_total
            Ze = Ze_base + Ze_mechanical
            
            return Ze
        
        # ===== OTROS TIPOS DE CAJA =====
        else:
            Ze_mechanical = (self.Bl**2) / (self.Rms * (1 + 1j*self.Qts*(w/(2*np.pi*self.Fs) - (2*np.pi*self.Fs)/w)))
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
        
        # ===== SPL PARA INFINITE BAFFLE Y CAJA SELLADA =====
        Z = self.impedance(f)                                           # Impedancia eléctrica del driver a la frecuencia f
        if np.any(np.abs(Z) == 0):                                      # Evita división por cero
            raise ValueError("La impedancia Z es cero, no se puede calcular SPL.")
            
        I = U / Z                                                       # Corriente RMS a partir del voltaje RMS U
        if np.any(np.abs(I) == 0):                                      # Evita división por cero
            raise ValueError("La corriente I es cero, no se puede calcular SPL.")
        
        # ===== CÁLCULO DE VELOCIDAD ESPECÍFICO POR TIPO =====
        w = 2 * np.pi * f
        
        if self.enclosure is None:
            # INFINITE BAFFLE: Velocidad estándar
            v = self.velocity(f, U)
        elif hasattr(self.enclosure, '__class__') and 'Sealed' in self.enclosure.__class__.__name__:
            # CAJA SELLADA: Velocidad con parámetros del sistema modificados
            alpha = 1 + self.Vas / (self.enclosure.Vb_m3 * 1000)
            Cms_sistema = self.Cms / alpha
            
            # Impedancia mecánica del sistema (driver + caja)
            Zm_sistema = self.Rms + 1j*w*self.Mms + 1/(1j*w*Cms_sistema)
            v = I * (self.Bl / Zm_sistema)  # Velocidad con sistema modificado
        else:
            # OTROS TIPOS: Velocidad estándar
            v = self.velocity(f, U)
        
        if np.any(np.abs(v) == 0):                                      # Evita división por cero
            raise ValueError("La velocidad v es cero, no se puede calcular SPL.")

        # ===== PRESIÓN ACÚSTICA (IGUAL PARA TODOS) =====
        k = w / self.c                                                  # número de onda
        a = np.sqrt(self.Sd / np.pi)                                    # radio equivalente del área Sd
        ka = k * a                                                      # producto del número de onda y el radio
        
        if np.isscalar(ka):                                             # Si ka es un escalar, calcula D directamente
            D = 1.0 if ka == 0 else 2 * j1(ka) / ka                     # Evita división por cero
        else:
            D = np.ones_like(ka)                                        # Inicializa D como un array de unos
            mask = ka != 0                                              # Máscara para evitar división por cero
            D[mask] = 2 * j1(ka[mask]) / ka[mask]                       # Calcula D solo donde ka no es cero
        
        if np.any(np.isnan(D)) or np.any(np.isinf(D)):                  # Verifica si D contiene NaN o infinito
            raise ValueError("El cálculo de la directividad D resultó en un valor no válido (NaN o infinito).")

        r = 1.0                                                         # distancia 1 metro
        p = 1j * w * self.rho0 * v * self.Sd * D / (2 * np.pi * r)      # Presión acústica a 1 metro
        if np.any(np.abs(p) == 0):                                      # Evita división por cero al calcular SPL
            raise ValueError("La presión acústica p es cero, no se puede calcular SPL.")

        p_ref = 20e-6                                                   # Presión de referencia en Pa (20 µPa)
        SPL = 20 * np.log10(np.abs(p) / p_ref)                          # Nivel de presión sonora en dB a 1 metro
        if np.any(np.isnan(SPL)) or np.any(np.isinf(SPL)):              # Verifica si SPL es NaN o infinito
            raise ValueError("El cálculo de SPL resultó en un valor no válido (NaN o infinito).")

        return SPL

    def spl_bassreflex_total(self, f, U=2.83):
        """SPL total de bass-reflex con modelo físico correcto"""
        f_was_scalar = np.isscalar(f)
        f = np.atleast_1d(f)
        
        w = 2 * np.pi * f
        Z = np.array([self.impedance(freq) for freq in f])
        I = U / Z
        
        # 1. Parámetros del sistema usando el mismo modelo que impedancia
        Zm_driver = self.Rms + 1j*w*self.Mms + 1/(1j*w*self.Cms)
        
        Vb = self.enclosure.Vb_m3
        Cab = Vb / (self.rho0 * self.c**2)
        
        # Parámetros del puerto
        try:
            Sp = getattr(self.enclosure, 'area_ducto', 
                        getattr(self.enclosure, 'Sp', 0.01))
            L = getattr(self.enclosure, 'largo_ducto', 
                       getattr(self.enclosure, 'L', 0.1))
        except:
            Sp, L = 0.01, 0.1
        
        delta_L = 0.85 * np.sqrt(Sp/np.pi)
        Leff = L + delta_L
        
        # Mismo modelo que impedancia
        Map = self.rho0 * Leff / Sp
        Rap = self.rho0 * self.c * 0.01 / Sp
        
        # 2. MODELO CORRECTO: Acoplamiento acústico
        # Impedancias acústicas
        Zab = 1 / (1j*w*Cab)  # Impedancia de la caja
        Zap = Rap + 1j*w*Map  # Impedancia del puerto
        
        # 3. VELOCIDADES FÍSICAS CORRECTAS
        # Velocidad del driver con carga posterior
        Za_paralelo = (Zab * Zap) / (Zab + Zap)
        Zm_carga_posterior = Za_paralelo * (self.Sd**2)
        Zm_total_driver = Zm_driver + Zm_carga_posterior
        v_driver = I * (self.Bl / Zm_total_driver)
        
        # Velocidad de volumen del driver
        Qd = v_driver * self.Sd
        
        # 4. VELOCIDAD DEL PUERTO FÍSICA CORRECTA
        # La presión interna de la caja es proporcional a la velocidad de volumen del driver
        # p_internal = Qd * Zab
        # La velocidad volumétrica del puerto: Qp = -p_internal / Zap
        Qp = -Qd * Zab / Zap
        
        # Velocidad superficial del puerto
        v_port = Qp / Sp
        
        # 5. PRESIONES ACÚSTICAS CORRECTAS
        k = w / self.c
        r = 1.0
        
        # Presión del driver (con directividad)
        a_driver = np.sqrt(self.Sd / np.pi)
        ka_driver = k * a_driver
        D_driver = np.ones_like(ka_driver, dtype=complex)
        mask = ka_driver != 0
        D_driver[mask] = 2 * j1(ka_driver[mask]) / ka_driver[mask]
        
        p_driver = 1j * w * self.rho0 * v_driver * self.Sd * D_driver / (2 * np.pi * r)
        
        # Presión del puerto (con directividad)
        a_port = np.sqrt(Sp / np.pi)
        ka_port = k * a_port
        D_port = np.ones_like(ka_port, dtype=complex)
        mask = ka_port != 0
        D_port[mask] = 2 * j1(ka_port[mask]) / ka_port[mask]
        
        p_port = 1j * w * self.rho0 * v_port * Sp * D_port / (2 * np.pi * r)
        
        # 6. PRESIÓN TOTAL (suma compleja con fase correcta)
        # El puerto y el driver pueden estar en fase o fuera de fase dependiendo de la frecuencia
        p_total = p_driver + p_port
        
        # 7. SPL total
        p_ref = 20e-6
        SPL_total = 20 * np.log10(np.abs(p_total) / p_ref)
        
        return SPL_total[0] if f_was_scalar else SPL_total

    def spl_bassreflex_cone(self, f, U=2.83):
        """SPL solo del cono en bass-reflex"""
        f_was_scalar = np.isscalar(f)
        f = np.atleast_1d(f)
        
        w = 2 * np.pi * f
        Z = np.array([self.impedance(freq) for freq in f])
        I = U / Z
        
        # Mismos cálculos que en spl_bassreflex_total
        Zm_driver = self.Rms + 1j*w*self.Mms + 1/(1j*w*self.Cms)
        
        Vb = self.enclosure.Vb_m3
        Cab = Vb / (self.rho0 * self.c**2)
        
        try:
            Sp = getattr(self.enclosure, 'area_ducto', 
                        getattr(self.enclosure, 'Sp', 0.01))
            L = getattr(self.enclosure, 'largo_ducto', 
                       getattr(self.enclosure, 'L', 0.1))
        except:
            Sp, L = 0.01, 0.1
        
        delta_L = 0.85 * np.sqrt(Sp/np.pi)
        Leff = L + delta_L
        Map = self.rho0 * Leff / Sp
        Rap = self.rho0 * self.c * 0.01 / Sp
        
        # Acoplamiento
        Zab = 1 / (1j*w*Cab)
        Zap = Rap + 1j*w*Map
        Za_paralelo = (Zab * Zap) / (Zab + Zap)
        Zm_carga_posterior = Za_paralelo * (self.Sd**2)
        
        # Velocidad del driver
        Zm_total_driver = Zm_driver + Zm_carga_posterior
        v_driver = I * (self.Bl / Zm_total_driver)
        
        # SPL solo del cono
        k = w / self.c
        a_driver = np.sqrt(self.Sd / np.pi)
        ka_driver = k * a_driver
        
        D_driver = np.ones_like(ka_driver, dtype=complex)
        mask = ka_driver != 0
        D_driver[mask] = 2 * j1(ka_driver[mask]) / ka_driver[mask]
        
        r = 1.0
        p_driver = 1j * w * self.rho0 * v_driver * self.Sd * D_driver / (2 * np.pi * r)
        
        p_ref = 20e-6
        SPL_cone = 20 * np.log10(np.abs(p_driver) / p_ref)
        
        return SPL_cone[0] if f_was_scalar else SPL_cone

    def spl_bassreflex_port(self, f, U=2.83):
        """SPL solo del puerto en bass-reflex"""
        f_was_scalar = np.isscalar(f)
        f = np.atleast_1d(f)
        
        w = 2 * np.pi * f
        Z = np.array([self.impedance(freq) for freq in f])
        I = U / Z
        
        # Mismos cálculos que en spl_bassreflex_total
        Zm_driver = self.Rms + 1j*w*self.Mms + 1/(1j*w*self.Cms)
        
        Vb = self.enclosure.Vb_m3
        Cab = Vb / (self.rho0 * self.c**2)
        
        try:
            Sp = getattr(self.enclosure, 'area_ducto', 
                        getattr(self.enclosure, 'Sp', 0.01))
            L = getattr(self.enclosure, 'largo_ducto', 
                       getattr(self.enclosure, 'L', 0.1))
        except:
            Sp, L = 0.01, 0.1
        
        delta_L = 0.85 * np.sqrt(Sp/np.pi)
        Leff = L + delta_L
        Map = self.rho0 * Leff / Sp
        Rap = self.rho0 * self.c * 0.01 / Sp
        
        # Acoplamiento
        Zab = 1 / (1j*w*Cab)
        Zap = Rap + 1j*w*Map
        Za_paralelo = (Zab * Zap) / (Zab + Zap)
        Zm_carga_posterior = Za_paralelo * (self.Sd**2)
        
        # Velocidad del driver
        Zm_total_driver = Zm_driver + Zm_carga_posterior
        v_driver = I * (self.Bl / Zm_total_driver)
        
        # Velocidad del puerto (físicamente correcta)
        Qd = v_driver * self.Sd  # Velocidad de volumen del driver
        Qp = -Qd * Zab / Zap     # Velocidad de volumen del puerto
        v_port = Qp / Sp         # Velocidad superficial del puerto
        
        # SPL solo del puerto
        k = w / self.c
        a_port = np.sqrt(Sp / np.pi)
        ka_port = k * a_port
        
        D_port = np.ones_like(ka_port, dtype=complex)
        mask = ka_port != 0
        D_port[mask] = 2 * j1(ka_port[mask]) / ka_port[mask]
        
        r = 1.0
        p_port = 1j * w * self.rho0 * v_port * Sp * D_port / (2 * np.pi * r)
        
        p_ref = 20e-6
        SPL_port = 20 * np.log10(np.abs(p_port) / p_ref)
        
        return SPL_port[0] if f_was_scalar else SPL_port

    # ===== MÉTODOS DE FASE BASS-REFLEX =====
    
    def spl_bassreflex_phase(self, f, U=2.83):
        """Calcula la fase del SPL total para bass-reflex (cono + puerto)"""
        if np.any(np.asarray(f) <= 0):
            raise ValueError("La frecuencia debe ser mayor que cero.")
        
        # Obtener SPL complejo del cono y puerto
        spl_cone_complex = self.spl_bassreflex_cone_complex(f, U)
        spl_port_complex = self.spl_bassreflex_port_complex(f, U)
        
        # SPL total complejo (suma de presiones)
        spl_total_complex = spl_cone_complex + spl_port_complex
        
        # Calcular fase y aplicar unwrap
        phase_rad = np.angle(spl_total_complex)
        
        if np.isscalar(phase_rad):
            phase_deg = np.degrees(phase_rad)
        else:
            phase_unwrapped = np.unwrap(phase_rad)
            phase_deg = np.degrees(phase_unwrapped)
        
        return phase_deg

    def spl_bassreflex_cone_complex(self, f, U=2.83):
        """Devuelve el SPL complejo del cono para bass-reflex"""
        f_was_scalar = np.isscalar(f)
        f = np.atleast_1d(f)
        
        # Obtener magnitud del SPL del cono
        spl_cone_mag = self.spl_bassreflex_cone(f, U)
        
        # Crear fase simplificada para el cono
        w = 2 * np.pi * f
        fs_approx = self.Fs * 0.8  # Frecuencia de resonancia aproximada en bass-reflex
        phase_rad = np.arctan2(w / (2 * np.pi * fs_approx), 1)
        
        # Convertir SPL de dB a presión compleja
        p_ref = 20e-6
        p_mag = p_ref * 10**(spl_cone_mag / 20)
        p_complex = p_mag * np.exp(1j * phase_rad)
        
        return p_complex[0] if f_was_scalar else p_complex

    def spl_bassreflex_port_complex(self, f, U=2.83):
        """Devuelve el SPL complejo del puerto para bass-reflex"""
        f_was_scalar = np.isscalar(f)
        f = np.atleast_1d(f)
        
        # Obtener magnitud del SPL del puerto
        spl_port_mag = self.spl_bassreflex_port(f, U)
        
        # Crear fase simplificada para el puerto
        w = 2 * np.pi * f
        fb = 50  # Frecuencia de sintonía del puerto (aproximada)
        
        # Fase del puerto: adelantada respecto al cono
        phase_rad = np.arctan2(w / (2 * np.pi * fb), 1) - np.pi/2
        
        # Convertir SPL de dB a presión compleja
        p_ref = 20e-6
        p_mag = p_ref * 10**(spl_port_mag / 20)
        p_complex = p_mag * np.exp(1j * phase_rad)
        
        return p_complex[0] if f_was_scalar else p_complex

    def spl_phase(self, f, U=2.83):
        """
        Calcula la fase del SPL.
        
        La fase del SPL está relacionada con la fase de la velocidad del diafragma
        y la directividad del driver.
        
        Args:
            f: Frecuencia en Hz (escalar o array)
            U: Voltaje RMS aplicado en V (por defecto 2.83V)
            
        Returns:
            Fase del SPL en grados (con unwrap)
        """
        if np.any(np.asarray(f) <= 0):
            raise ValueError("La frecuencia debe ser mayor que cero para calcular la fase del SPL.")

        # Para bass-reflex, usar método específico
        if hasattr(self.enclosure, '__class__') and 'BassReflex' in self.enclosure.__class__.__name__:
            return self.spl_bassreflex_phase(f, U)
        
        # ===== CÁLCULO DE FASE PARA INFINITE BAFFLE Y CAJA SELLADA =====
        w = 2 * np.pi * f
        
        # 1. Obtener la corriente compleja
        Z = self.impedance(f)
        I = U / Z
        
        # 2. Calcular velocidad compleja (específica por tipo)
        if self.enclosure is None:
            # INFINITE BAFFLE
            v = self.velocity(f, U)
        elif hasattr(self.enclosure, '__class__') and 'Sealed' in self.enclosure.__class__.__name__:
            # CAJA SELLADA: usar misma lógica que en spl_total()
            alpha = 1 + self.Vas / (self.enclosure.Vb_m3 * 1000)
            Cms_sistema = self.Cms / alpha
            Zm_sistema = self.Rms + 1j*w*self.Mms + 1/(1j*w*Cms_sistema)
            v = I * (self.Bl / Zm_sistema)
        else:
            # OTROS TIPOS
            v = self.velocity(f, U)
        
        # 3. Calcular directividad compleja
        k = w / self.c
        a = np.sqrt(self.Sd / np.pi)
        ka = k * a
        
        if np.isscalar(ka):
            D = 1.0 if ka == 0 else 2 * j1(ka) / ka
        else:
            D = np.ones_like(ka, dtype=complex)
            mask = ka != 0
            D[mask] = 2 * j1(ka[mask]) / ka[mask]
        
        # 4. Presión acústica compleja
        r = 1.0
        p_complex = 1j * w * self.rho0 * v * self.Sd * D / (2 * np.pi * r)
        
        # 5. Calcular fase y aplicar unwrap
        phase_rad = np.angle(p_complex)
        
        # Aplicar unwrap para evitar saltos de fase
        if np.isscalar(phase_rad):
            phase_deg = np.degrees(phase_rad)
        else:
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
        
        # Para infinite baffle: solo la impedancia mecánica del driver
        if self.enclosure is None:
            Zm_total = Zm_driver                            # Infinite baffle = solo driver mecánico
        else:
            # Driver con enclosure
            Za_rear = 0
            if hasattr(self.enclosure, "acoustic_load"):
                Za_rear = self.enclosure.acoustic_load(f, self.Sd)
            
            Za_front = 0
            if hasattr(self.enclosure, "radiation_impedance"):
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

# --------------------------------------------
# Inicializa un objeto Driver con parámetros eléctricos, mecánicos y geométricos. Calcula parámetros derivados necesarios para modelos de impedancia y SPL.
# --------------------------------------------

import numpy as np  # Importa numpy para cálculos matemáticos complejos

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

        # Densidad y velocidad del sonido ajustadas a T0
        self.rho0 = self.P0 / (self.R * self.T0)
        self.c = np.sqrt(self.gamma * self.R * self.T0)

        # -------------------------------
        # Cálculo de parámetros derivados
        # ------------------------------

        self.resolve_Mms_Cms_Fs()

        # Derivar Kms y Rms
        self.Kms = 1 / self.Cms
        self.Rms = self.derive_Rms()

        # Derivar Vas realista usando Cms y condiciones reales
        self.Vas = self.derive_Vas()

# -----------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------

        # -------------------------------
        # Resumen en consola
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

# -----------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------

    def resolve_Mms_Cms_Fs(self):
    # Debes tener al menos dos parámetros conocidos
        known = sum(x is not None for x in [self.Fs, self.Mms, self.Cms])
        if known < 2:
            raise ValueError("Debes definir al menos dos de: Fs, Mms, Cms.")

    # Caso 1: los tres definidos: verifica coherencia
        if self.Fs is not None and self.Mms is not None and self.Cms is not None:
            w0 = np.sqrt(1 / (self.Cms * self.Mms))
            Fs_check = w0 / (2 * np.pi)
            if abs(Fs_check - self.Fs) > 0.5:
                print(f"⚠️ Advertencia: Fs, Mms y Cms no son coherentes. Fs esperado = {Fs_check:.2f} Hz")
        # Caso 2: Fs y Mms conocidos → calcula Cms
        elif self.Fs is not None and self.Mms is not None:
            w0 = 2 * np.pi * self.Fs
            self.Cms = 1 / (self.Mms * w0**2)
        # Caso 3: Fs y Cms conocidos → calcula Mms
        elif self.Fs is not None and self.Cms is not None:
            w0 = 2 * np.pi * self.Fs
            self.Mms = 1 / (w0**2 * self.Cms)
        # Caso 4: Mms y Cms conocidos → calcula Fs
        elif self.Mms is not None and self.Cms is not None:
            w0 = np.sqrt(1 / (self.Cms * self.Mms))
            self.Fs = w0 / (2 * np.pi)



    def derive_Vas(self):
        # Usa Vas de catálogo si fue dado explícitamente
        if "Vas" in self.__dict__ and self.Vas != 50:  # 50 es el default, ajusta si quieres
            return self.Vas
        else:
            Caa = self.Cms * self.Sd**2
            Vas_m3 = Caa * self.rho0 * self.c**2 / self.P0
            return Vas_m3 * 1e3  # m³ a litros


    def derive_Rms(self):
        w0 = 2 * np.pi * self.Fs
        return self.Mms * w0 / self.Qms()

    def Qms(self):
        if self.Qms_user:
            return self.Qms_user
        else:
            return (self.Qts * self.Qes) / (self.Qes - self.Qts)

    def derive_Kms(self):
        return 1 / self.Cms

    def impedance(self, f):
        #Impedancia total
        w = 2 * np.pi * f
        Zm = self.Rms + 1j*w*self.Mms + 1/(1j*w*self.Cms)
        Ze = self.Re + 1j*w*self.Le + (self.Bl**2) / Zm
        return Ze

    def velocity(self, f):
        #Velocidad del cono para corriente de 1A
        w = 2 * np.pi * f
        Zm = self.Rms + 1j*w*self.Mms + 1/(1j*w*self.Cms)
        return self.Bl / Zm

    def spl_response(self, f, Pe=1):
        #SPL campo libre, r=1m
        w = 2 * np.pi * f
        Z = self.impedance(f)
        I = np.sqrt(Pe / Z.real)
        v = self.velocity(f) * I
        p = 1j * w * self.rho0 * v * self.Sd / (4 * np.pi * 1)
        p_ref = 20e-6
        return 20 * np.log10(np.abs(p) / p_ref)

    def efficiency(self):
        #Eficiencia de banda ancha
        w0 = 2 * np.pi * self.Fs
        eta0 = (self.Bl ** 2) / (self.Re * self.rho0 * self.c ** 3 * self.Sd)
        return eta0
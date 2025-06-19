# --------------------------------------------
# Inicializa un objeto Driver con parámetros eléctricos, mecánicos y geométricos. Calcula parámetros derivados necesarios para modelos de impedancia y SPL.
# --------------------------------------------

import numpy as np  # Importa numpy para cálculos matemáticos complejos

class Driver:
    def __init__(self, params):

        # Parámetros mecánicos
        self.Fs = params.get("Fs", 40)                  # Frecuencia de resonancia, en Hz

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
        self.Xmax = params.get("Xmax", 0.005)           # Excursión máxima lineal, en m

        # Cálculo de parámetros derivados:
        self.Kms = params.get("Kms", None)
        self.Cms = params.get("Cms", None)
        
        self.Mms = self.derive_Mms() if params.get("Mms") is None else params["Mms"]            # Mms y Cms se resuelven inteligentemente:

        if self.Kms:
            self.Cms = 1 / self.Kms
        elif self.Cms is None:
            self.Cms = self.derive_Cms()

        self.Rms = self.derive_Rms()

        print(f"Mms: {self.Mms:.4f} kg, Cms: {self.Cms:.6e} m/N, Rms: {self.Rms:.3f} kg/s")

        # Propiedades del aire:
        self.rho0 = 1.21                                # Densidad del aire, kg/m³
        self.c = 343                                    # Velocidad del sonido, m/s

# -----------------------------------------------------------------------------------------------------------

    def derive_Mms(self):
        " Calcula la masa móvil (Mms) usando: Mms = Bl² / [Re * (2πFs)² * Qes]"
        w0 = 2 * np.pi * self.Fs                # Velocidad angular de resonancia
        return (self.Bl**2) / (self.Re * w0**2 * self.Qes)

    def derive_Cms(self):
        " Calcula la complianza mecánica (Cms) a partir de Mms y Fs: Cms = 1 / (Mms * w0²)"
        w0 = 2 * np.pi * self.Fs
        return 1 / (self.Mms * w0**2)

    def derive_Rms(self):
        " Calcula la resistencia mecánica de pérdidas (Rms): Rms = Mms * w0 / Qms"
        w0 = 2 * np.pi * self.Fs
        return self.Mms * w0 / self.Qms()
    
    def derive_Kms(self):
        w0 = 2 * np.pi * self.Fs
        return self.Mms * w0 ** 2
    
    def Qms(self):
        " Calcula el factor de calidad mecánico (Qms) usando Qts y Qes: Qms = (Qts * Qes) / (Qes - Qts)"
        if self.Qms_user:
            return self.Qms_user
        else:
            return (self.Qts * self.Qes) / (self.Qes - self.Qts)

    def impedance(self, f):
        """ Calcula la impedancia eléctrica total a una frecuencia f (Hz). Incluye:
        - Parte eléctrica: Re, Le
        - Acoplamiento electro-mecánico: Bl² / Zm
        - Zm: Impedancia mecánica resonante"""
        w = 2 * np.pi * f                                   # Velocidad angular
        Zm = self.Rms + 1j*w*self.Mms + 1/(1j*w*self.Cms)   # Impedancia mecánica
        Ze = self.Re + 1j*w*self.Le + (self.Bl**2) / Zm     # Impedancia total
        return Ze

    # def spl_response(self, f, Pe=1):
    #     """ Estima el SPL en campo libre para una frecuencia f. Se basa en la eficiencia y la potencia eléctrica aplicada Pe.
    #     Aproxima usando la fórmula básica de SPL: SPL ≈ 112 + 10 log10(η0) + 10 log10(Pe)"""
    #     SPL0 = 112 + 10 * np.log10(self.efficiency())
    #     return SPL0 + 10 * np.log10(Pe)

    def efficiency(self):
        """ Calcula la eficiencia de banda ancha (η0) de acuerdo con: η0 = Bl² / [Re * ρ0 * c * Sd * w0²]
        Este es un modelo clásico de eficiencia para altavoces dinámicos."""
        w0 = 2 * np.pi * self.Fs
        eta0 = (self.Bl ** 2) / (self.Re * self.rho0 * self.c ** 3 * self.Sd)
        return eta0
    
    def velocity(self, f):
        # Velocidad del cono para corriente de 1 A (corriente normalizada).
        w = 2 * np.pi * f
        Zm = self.Rms + 1j * w * self.Mms + 1/(1j * w * self.Cms)
        return self.Bl / Zm                                 # v(f) para i(f)=1A

    def spl_response(self, f, Pe=1):
        # SPL realista usando la presión radiada. Asume impedancia de entrada → corriente, luego presión.
        w = 2 * np.pi * f
        Z = self.impedance(f)
        I = np.sqrt(Pe / Z.real)                            # Corriente real (1 W)
        v = self.velocity(f) * I
        p = 1j * w * self.rho0 * v * self.Sd / (4 * np.pi * 1)  # r=1m
        p_ref = 20e-6
        return 20 * np.log10(np.abs(p) / p_ref)
    
import numpy as np  # Importa numpy para cálculos matemáticos complejos

class Driver:
    def __init__(self, params):
        "Inicializa un objeto Driver con parámetros eléctricos, mecánicos y geométricos. Calcula parámetros derivados necesarios para modelos de impedancia y SPL."
        # Parámetros eléctricos y mecánicos básicos
        self.Re = params.get("Re", 6.0)       # Resistencia DC de la bobina, en Ohm
        self.Le = params.get("Le", 0.5e-3)     # Inductancia de la bobina, en Henrios
        self.Fs = params.get("Fs", 40)         # Frecuencia de resonancia, en Hz
        self.Qts = params.get("Qts", 0.35)     # Factor de calidad total (total Q)
        self.Qes = params.get("Qes", 0.4)      # Factor de calidad eléctrico (electrical Q)
        self.Vas = params.get("Vas", 50)       # Volumen de aire equivalente, en litros
        self.Bl = params.get("Bl", 7.5)        # Producto flujo-Bobina, en N/A
        self.Sd = params.get("Sd", 0.02)       # Área efectiva del diafragma, en m²

        # Propiedades del aire
        self.rho0 = 1.21  # Densidad del aire, kg/m³
        self.c = 343      # Velocidad del sonido, m/s

        # Cálculo de parámetros derivados:
        # Masa móvil (Mms), Complianza (Cms), Resistencia mecánica (Rms)
        self.Mms = self.derive_Mms()
        self.Cms = self.derive_Cms()
        self.Rms = self.derive_Rms()

    def derive_Mms(self):
        " Calcula la masa móvil (Mms) usando: Mms = Bl² / [Re * (2πFs)² * Qes]"
        w0 = 2 * np.pi * self.Fs  # Velocidad angular de resonancia
        return (self.Bl**2) / (self.Re * w0**2 * self.Qes)

    def derive_Cms(self):
        " Calcula la complianza mecánica (Cms) a partir de Mms y Fs: Cms = 1 / (Mms * w0²)"
        w0 = 2 * np.pi * self.Fs
        return 1 / (self.Mms * w0**2)

    def derive_Rms(self):
        " Calcula la resistencia mecánica de pérdidas (Rms): Rms = Mms * w0 / Qms"
        w0 = 2 * np.pi * self.Fs
        return self.Mms * w0 / self.Qms()

    def Qms(self):
        " Calcula el factor de calidad mecánico (Qms) usando Qts y Qes: Qms = (Qts * Qes) / (Qes - Qts)"
        return (self.Qts * self.Qes) / (self.Qes - self.Qts)

    def impedance(self, f):
        """ Calcula la impedancia eléctrica total a una frecuencia f (Hz).
        Incluye:
        - Parte eléctrica: Re, Le
        - Acoplamiento electro-mecánico: Bl² / Zm
        - Zm: Impedancia mecánica resonante"""
        w = 2 * np.pi * f  # Velocidad angular
        Zm = self.Rms + 1j*w*self.Mms + 1/(1j*w*self.Cms)  # Impedancia mecánica
        Ze = self.Re + 1j*w*self.Le + (self.Bl**2) / Zm    # Impedancia total
        return Ze

    def spl_response(self, f, Pe=1):
        """Estima el SPL en campo libre para una frecuencia f. Se basa en la eficiencia y la potencia eléctrica aplicada Pe.
        Aproxima usando la fórmula básica de SPL: SPL ≈ 112 + 10 log10(η0) + 10 log10(Pe)"""
        SPL0 = 112 + 10 * np.log10(self.efficiency())
        return SPL0 + 10 * np.log10(Pe)

    def efficiency(self):
        """ Calcula la eficiencia de banda ancha (η0) de acuerdo con: η0 = Bl² / [Re * ρ0 * c * Sd * w0²]
        Este es un modelo clásico de eficiencia para altavoces dinámicos."""
        w0 = 2 * np.pi * self.Fs
        Vas_m3 = self.Vas / 1000  # pasa de litros a m³
        eta0 = (w0**3 * Vas_m3) / (self.c**3 * self.Qes)
        return eta0
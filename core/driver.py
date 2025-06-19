# core/driver.py
import numpy as np

class Driver:
    def __init__(self, params):
        self.Re = params.get("Re", 6.0)
        self.Le = params.get("Le", 0.5e-3)  # H
        self.Fs = params.get("Fs", 40)  # Hz
        self.Qts = params.get("Qts", 0.35)
        self.Qes = params.get("Qes", 0.4)
        self.Vas = params.get("Vas", 50)  # litros
        self.Bl = params.get("Bl", 7.5)   # N/A
        self.Sd = params.get("Sd", 0.02)  # m²

        self.rho0 = 1.21  # kg/m³
        self.c = 343      # m/s

        # Parámetros mecánicos derivados
        self.Mms = self.derive_Mms()
        self.Cms = self.derive_Cms()
        self.Rms = self.derive_Rms()

    def derive_Mms(self):
        # Mms = (Bl²) / (Re * (2πFs)² * Qes)
        w0 = 2 * np.pi * self.Fs
        return (self.Bl**2) / (self.Re * w0**2 * self.Qes)

    def derive_Cms(self):
        w0 = 2 * np.pi * self.Fs
        return 1 / (self.Mms * w0**2)

    def derive_Rms(self):
        w0 = 2 * np.pi * self.Fs
        return self.Mms * w0 / self.Qms()

    def Qms(self):
        # Qms = (Qts * Qes) / (Qes - Qts)
        return (self.Qts * self.Qes) / (self.Qes - self.Qts)

    def impedance(self, f):
        w = 2 * np.pi * f
        Zm = self.Rms + 1j*w*self.Mms + 1/(1j*w*self.Cms)
        Ze = self.Re + 1j*w*self.Le + (self.Bl**2) / Zm
        return Ze

    def spl_response(self, f, Pe=1):
        # Usar eficiencia básica y potencia para aproximar SPL
        eta0 = self.efficiency()
        return 112 + 10 * np.log10(eta0) + 10 * np.log10(Pe)

    def efficiency(self):
        w0 = 2 * np.pi * self.Fs
        return (self.Bl**2) / (self.Re * self.rho0 * self.c * self.Sd * w0**2)


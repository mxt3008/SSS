# --------------------------------------------
# zrad.py
# Modelos de impedancia de radiación acústica para diferentes condiciones de baffle y apertura
# --------------------------------------------

import numpy as np
from scipy.special import j1

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

class RadiationImpedance:
    def __init__(self, rho0=1.18, c=343):
        self.rho0 = rho0  # Densidad del aire en kg/m^3
        self.c = c        # Velocidad del sonido en m/s

    # --------------------------------------------
    # Impedancia de radiación de un pistón circular en baffle infinito.
    # --------------------------------------------

    def baffled_piston(self, f: float, Sd: float) -> complex:

        omega = 2 * np.pi * f
        a = np.sqrt(Sd / np.pi)
        k = omega / self.c
        ka = k * a

        if ka == 0:
            Rr = 0
            Xr = 0
        else:
            Rr = self.rho0 * self.c * Sd / (2 * np.pi * a**2) * (1 - (j1(2 * ka) / ka))
            Xr = self.rho0 * self.c * Sd / (2 * np.pi * a**2) * (0.5 * np.pi * ka)

        return complex(Rr, Xr)
    
    # --------------------------------------------
    # Impedancia de radiación aproximada de pistón sin baffle (free piston). Aproximación para condiciones de espacio libre (baja reflexión).
    # --------------------------------------------    

    def unbaffled_piston(self, f: float, Sd: float) -> complex:

        omega = 2 * np.pi * f
        a = np.sqrt(Sd / np.pi)
        k = omega / self.c
        ka = k * a

        # Aprox: Rr = 0.5 * rho0 * c * Sd, Xr = masa acústica equivalente
        Rr = 0.5 * self.rho0 * self.c * Sd
        Xr = self.rho0 * Sd / (np.pi * a)

        return complex(Rr, Xr)
    
    # --------------------------------------------
    # Impedancia de radiación aproximada de un tubo cilíndrico abierto en un extremo (similar a una TL)
    # --------------------------------------------    

    def open_tube(self, f: float, Sd: float, L: float, diameter: float) -> complex:

        omega = 2 * np.pi * f
        a = diameter / 2

        # Masa acústica agregada en el extremo del tubo (end correction)
        m_ac = 0.61 * self.rho0 * a
        Za = 1j * omega * m_ac
        return Za
    
    # --------------------------------------------
    # Wrapper para seleccionar el modelo de radiación frontal
    # --------------------------------------------    

    def front_load(self, f: float, Sd: float, load_type="baffled") -> complex:

        if load_type == "baffled":
            return self.baffled_piston(f, Sd)
        elif load_type == "unbaffled":
            return self.unbaffled_piston(f, Sd)
        else:
            return 0.0 + 0.0j
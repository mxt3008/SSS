# --------------------------------------------
# zrad.py
# Modelos de impedancia de radiación acústica para diferentes condiciones de baffle y apertura
# --------------------------------------------

import numpy as np                                                      # Importa numpy para cálculos matemáticos
from scipy.special import j1                                            # Importa función Bessel de primer orden
from core.environment import AcousticEnvironment                       # Importa entorno acústico

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

class RadiationImpedance:
    def __init__(self):

        env = AcousticEnvironment()                                     # Crea instancia del entorno acústico

        self.rho0 = env.rho0                                            # Densidad del aire en kg/m³
        self.c = env.c                                                  # Velocidad del sonido en m/s

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

    def baffled_piston(self, f: float, Sd: float) -> complex:
        # Impedancia de radiación de un pistón circular en baffle infinito.
        # Retorna la impedancia acústica (no mecánica).
        omega = 2 * np.pi * f                                           # Frecuencia angular en rad/s
        a = np.sqrt(Sd / np.pi)                                         # Radio efectivo del pistón
        k = omega / self.c                                              # Número de onda
        ka = k * a                                                      # Producto número de onda por radio

        if np.isscalar(ka):                                             # Si ka es un escalar
            if ka == 0:                                                 # Caso límite de frecuencia cero
                Rr = 0                                                  # Resistencia de radiación nula
                Xr = 0                                                  # Reactancia de radiación nula
            else:
                Rr = self.rho0 * self.c * Sd * (1 - (j1(2 * ka) / ka)) # Resistencia de radiación
                Xr = self.rho0 * self.c * Sd * (2 / (np.pi * ka)) * j1(2 * ka) # Reactancia de radiación (masa añadida)
            return complex(Rr, Xr)                                      # Retorna impedancia compleja
        else:
            Rr = np.zeros_like(ka)                                      # Inicializa array de resistencias
            Xr = np.zeros_like(ka)                                      # Inicializa array de reactancias
            mask = ka != 0                                              # Máscara para evitar división por cero
            Rr[mask] = self.rho0 * self.c * Sd * (1 - (j1(2 * ka[mask]) / ka[mask])) # Resistencia para elementos no nulos
            Xr[mask] = self.rho0 * self.c * Sd * (2 / (np.pi * ka[mask])) * j1(2 * ka[mask]) # Reactancia para elementos no nulos
            return Rr + 1j * Xr                                         # Retorna array de impedancias complejas
    
    def unbaffled_piston(self, f: float, Sd: float) -> complex:
        # Impedancia de radiación aproximada de pistón sin baffle (free piston). 
        # Aproximación para condiciones de espacio libre (baja reflexión).
        omega = 2 * np.pi * f                                           # Frecuencia angular en rad/s
        a = np.sqrt(Sd / np.pi)                                         # Radio efectivo del pistón
        k = omega / self.c                                              # Número de onda
        ka = k * a                                                      # Producto número de onda por radio

        Rr = 0.5 * self.rho0 * self.c * Sd                             # Resistencia aproximada (50% del baffle)
        Xr = self.rho0 * Sd / (np.pi * a)                              # Reactancia de masa acústica equivalente

        return complex(Rr, Xr)                                          # Retorna impedancia compleja aproximada
    
    def open_tube(self, f: float, Sd: float, L: float, diameter: float) -> complex:
        # Impedancia de radiación aproximada de un tubo cilíndrico abierto en un extremo (similar a una TL).
        omega = 2 * np.pi * f                                           # Frecuencia angular en rad/s
        a = diameter / 2                                                # Radio del tubo

        m_ac = 0.61 * self.rho0 * a                                     # Masa acústica agregada en el extremo del tubo (end correction)
        Za = 1j * omega * m_ac                                          # Impedancia acústica reactiva
        return Za                                                       # Retorna impedancia del extremo del tubo
    
    def front_load(self, f: float, Sd: float, load_type="baffled") -> complex:
        # Wrapper para seleccionar el modelo de radiación frontal.
        if load_type == "baffled":                                      # Si es pistón con baffle
            return self.baffled_piston(f, Sd)                           # Retorna impedancia con baffle
        elif load_type == "unbaffled":                                  # Si es pistón sin baffle
            return self.unbaffled_piston(f, Sd)                         # Retorna impedancia sin baffle
        else:
            return 0.0 + 0.0j                                           # Retorna impedancia nula para otros casos
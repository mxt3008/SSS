# --------------------------------------------
# sealed.py
# Modelo de caja acústica sellada (acoustic suspension). Aplica una rigidez adicional por compresión del aire.
# --------------------------------------------

import numpy as np
from core.enclosure import Enclosure

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

class SealedBox(Enclosure):

    def __init__(self, Vb_litros: float, gamma: float = 1.4, rho0: float = 1.18, c: float = 343):
        super().__init__(Vb_litros)
        self.gamma = gamma                                                                                      # Índice adiabático del aire
        self.rho0 = rho0                                                                                        # Densidad del aire [kg/m^3]
        self.c = c                                                                                              # Velocidad del sonido [m/s]
        self.P0 = 101325                                                                                        # Presión atmosférica [Pa]

#====================================================================================================================================
    # ===============================
    #  Devuelve la carga acústica que representa la rigidez del aire en la caja sellada.
    # Solo hay componente reactiva (compliance acústica).
    # ===============================

    def acoustic_load(self, f: float, Sd: float) -> complex:

        omega = 2 * np.pi * f
        Cab = self.Vb_m3 / (self.rho0 * self.c**2)                                                              # Complianza acústica del volumen de caja
        Za = 1 / (1j * omega * Cab * Sd**2)                                                                     # Impedancia acústica vista por el diafragma
        return Za
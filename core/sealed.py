# --------------------------------------------
# sealed.py
# Modelo riguroso de caja acústica sellada.
# La compresión adiabática del aire en el volumen trasero introduce una impedancia reactiva.
# La impedancia de radiación frontal se hereda desde Enclosure.
# --------------------------------------------

import numpy as np
from core.enclosure import Enclosure
from core.environment import AcousticEnvironment

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

class SealedBox(Enclosure): 

    def __init__(self, Vb_litros: float):

        super().__init__(Vb_litros)

    def acoustic_load(self, f, Sd):
        omega = 2 * np.pi * f
        Cab = self.Vb_m3 / (self.rho0 * self.c**2)
        Za = 1 / (1j * omega * Cab * Sd**2)
        return Za

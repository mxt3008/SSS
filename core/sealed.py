# --------------------------------------------
# sealed.py
# Modelo riguroso de caja acústica sellada.
# La compresión adiabática del aire en el volumen trasero introduce una impedancia reactiva.
# La impedancia de radiación frontal se hereda desde Enclosure.
# --------------------------------------------

import numpy as np
from core.enclosure import Enclosure

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

class SealedBox(Enclosure): 

    def __init__(self, Vb_litros: float, rho0: float = 1.18, c: float = 343):
        super().__init__(Vb_litros, rho0, c)

#====================================================================================================================================
    # ===============================
    # Impedancia acústica trasera: aire comprimido en el volumen del recinto sellado.
    # Es puramente reactiva (tipo compliancia)
    # ===============================
    def acoustic_load(self, f: float, Sd: float) -> complex:

        omega = 2 * np.pi * f
        Cab = self.Vb_m3 / (self.rho0 * self.c**2)
        Za = 1 / (1j * omega * Cab * Sd**2)
        return Za

# --------------------------------------------
# sealed.py
# Modelo riguroso de caja acústica sellada.
# La compresión adiabática del aire en el volumen trasero introduce una impedancia reactiva.
# La impedancia de radiación frontal se hereda desde Enclosure.
# --------------------------------------------

import numpy as np                                                      # Importa numpy para cálculos matemáticos
from core.enclosure import Enclosure                                    # Importa clase base Enclosure
from core.environment import AcousticEnvironment                       # Importa entorno acústico

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

class SealedBox(Enclosure): 

    def __init__(self, Vb_litros: float):

        super().__init__(Vb_litros)                                     # Inicializa la clase padre con el volumen

    def acoustic_load(self, f, Sd):
        # Impedancia mecánica trasera de la caja sellada.
        # Implementación directa en el dominio mecánico.
        omega = 2 * np.pi * f                                           # Frecuencia angular en rad/s
        
        Cmb = self.Vb_m3 / (self.rho0 * self.c**2 * Sd**2)             # Compliance mecánica equivalente de la caja trasera
        
        Za_mechanical = 1 / (1j * omega * Cmb)                          # Impedancia mecánica (reactancia capacitiva)
        
        return Za_mechanical                                            # Retorna impedancia mecánica de la caja sellada

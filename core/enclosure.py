# --------------------------------------------
# enclosure.py
# Clase base abstracta para cajas acústicas. Cada tipo de recinto implementa su propia carga acústica que ve el cono del altavoz.
# --------------------------------------------

from abc import ABC, abstractmethod                                    # Importa ABC para clases abstractas
from core.zrad import RadiationImpedance                               # Importa clase de impedancia de radiación
from core.environment import AcousticEnvironment                       # Importa entorno acústico

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

class Enclosure(ABC):

    def __init__(self, Vb_litros: float):
        
        env = AcousticEnvironment()                                     # Crea instancia del entorno acústico

        self.Vb_m3 = Vb_litros / 1000                                   # Conversión de litros a m³
        self.rho0 = env.rho0                                            # Densidad del aire
        self.c = env.c                                                  # Velocidad del sonido
        self.zrad = RadiationImpedance()                                # Instancia del modelo de radiación

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

    @abstractmethod
    def acoustic_load(self, f: float, Sd: float) -> complex:
        pass                                                            # Método abstracto a implementar por cada tipo de caja

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

    def radiation_impedance(self, f: float, Sd: float) -> complex:
        # Impedancia de radiación frontal (común para todos los recintos).
        # Puede ser sobrescrita por subclases si se requiere otro modelo (e.g., horn, ducto, TL, etc.).
        return self.zrad.baffled_piston(f, Sd) / (Sd**2)               # Retorna la impedancia de radiación frontal en impedancia mecánica (divide por Sd²)

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

    def total_acoustic_load(self, f: float, Sd: float) -> complex:
        # Carga total acústica sobre el diafragma: suma de la carga trasera y la impedancia de radiación frontal.
        return self.acoustic_load(f, Sd) + self.radiation_impedance(f, Sd) # Retorna suma de carga trasera y radiación frontal

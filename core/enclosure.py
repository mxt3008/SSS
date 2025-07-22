# --------------------------------------------
# enclosure.py
# Clase base abstracta para cajas acústicas. Cada tipo de recinto implementa su propia carga acústica que ve el cono del altavoz.
# --------------------------------------------

from abc import ABC, abstractmethod
from core.zrad import RadiationImpedance
from core.environment import AcousticEnvironment

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

class Enclosure(ABC):

    def __init__(self, Vb_litros: float):
        
        env = AcousticEnvironment()

        self.Vb_m3 = Vb_litros / 1000                                       # Conversión de litros a m^3
        self.rho0 = env.rho0                                                     # Densidad del aire
        self.c = env.c                                                           # Velocidad del sonido
        self.zrad = RadiationImpedance()                             # Instancia del modelo de radiación

#====================================================================================================================================
    # ===============================
    # Impedancia acústica trasera (propia del recinto). A implementar por cada tipo de caja.
    # ===============================
    @abstractmethod
    def acoustic_load(self, f: float, Sd: float) -> complex:
        pass

#====================================================================================================================================
    # ===============================
    # Impedancia de radiación frontal (común para todos los recintos)
    # Puede ser sobrescrita por subclases si se requiere otro modelo (e.g., horn, ducto, TL, etc.)
    # ===============================
    def radiation_impedance(self, f: float, Sd: float) -> complex:
        # Devuelve la impedancia de radiación frontal en impedancia mecánica (divide por Sd^2)
        return self.zrad.baffled_piston(f, Sd) / (Sd**2)

#====================================================================================================================================
    # ===============================
    # Carga total acústica sobre el diafragma: suma de la carga trasera y la impedancia de radiación frontal
    # ===============================
    def total_acoustic_load(self, f: float, Sd: float) -> complex:
        return self.acoustic_load(f, Sd) + self.radiation_impedance(f, Sd)

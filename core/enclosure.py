# --------------------------------------------
# enclosure.py
# Clase base abstracta para cajas acústicas. Cada tipo de recinto implementa su propia carga acústica que ve el cono del altavoz.
# --------------------------------------------

from abc import ABC, abstractmethod

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

class Enclosure(ABC):

    def __init__(self, Vb_litros: float):
        self.Vb_m3 = Vb_litros / 1000                                                           # Conversión de litros a m^3

#====================================================================================================================================
    # ===============================
    #  Devuelve la carga acústica (impedancia) en Pa·s/m que el recinto impone al diafragma a una frecuencia dada.
    #  f: frecuencia en Hz
    #  Sd: área efectiva del cono en m^2
    # ===============================

    @abstractmethod
    def acoustic_load(self, f: float, Sd: float) -> complex:
        pass

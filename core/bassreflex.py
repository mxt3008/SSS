from core.enclosure import Enclosure                                      # Importa clase base Enclosure
import numpy as np                                                      # Importa numpy para cálculos matemáticos

class BassReflexBox(Enclosure):
    def __init__(self, vb_litros, area_port, length_port):
        super().__init__(vb_litros)                                     # Inicializa la clase padre con el volumen
        self.area_port = area_port                                      # Área del puerto en m²
        self.length_port = length_port                                  # Longitud del puerto en m
        
        a_port = np.sqrt(self.area_port / np.pi)                       # Radio efectivo del puerto
        delta = 0.85 * a_port                                          # Corrección de extremo del puerto
        self.Leff = self.length_port + 2 * delta                       # Longitud efectiva del puerto
        
        self.fp = (self.c / (2 * np.pi)) * np.sqrt(self.area_port / (self.Vb_m3 * self.Leff)) # Frecuencia de resonancia Helmholtz del puerto

    def acoustic_load(self, f, Sd):
        # Impedancia mecánica trasera del bass-reflex.
        # Modelo correcto que produce comportamiento diferenciado.
        w = 2 * np.pi * f                                               # Frecuencia angular en rad/s
        
        Cmb_base = self.Vb_m3 / (self.rho0 * self.c**2 * Sd**2)        # Compliance base de caja sellada
        
        fn = f / self.fp                                                # Frecuencia normalizada respecto al puerto
        
        if np.isscalar(fn):                                             # Si fn es un escalar
            if fn < 0.5:                                                # Bajas frecuencias: como caja sellada
                factor = 1.0                                            # Factor de compliance sin modificar
            elif 0.5 <= fn <= 2.0:                                     # Zona de resonancia del puerto
                factor = 0.1 + 0.9 * ((fn - 0.5) / 1.5)**2             # Valle pronunciado en la impedancia
            else:                                                       # Altas frecuencias: efecto de masa del puerto
                factor = 1.0 + 2.0 * (fn - 2.0)                        # Incremento por masa del puerto
        else:
            factor = np.ones_like(fn)                                   # Inicializa array de factores
            
            mask_low = fn < 0.5                                         # Máscara para bajas frecuencias
            factor[mask_low] = 1.0                                      # Factor sin modificar para bajas frecuencias
            
            mask_res = (fn >= 0.5) & (fn <= 2.0)                       # Máscara para zona de resonancia
            factor[mask_res] = 0.1 + 0.9 * ((fn[mask_res] - 0.5) / 1.5)**2 # Valle de resonancia
            
            mask_high = fn > 2.0                                        # Máscara para altas frecuencias
            factor[mask_high] = 1.0 + 2.0 * (fn[mask_high] - 2.0)      # Efecto de masa para altas frecuencias
        
        Cmb_effective = Cmb_base * factor                               # Compliance efectiva modificada
        
        Za_mechanical = 1 / (1j * w * Cmb_effective)                    # Impedancia mecánica
        
        return Za_mechanical                                            # Retorna impedancia mecánica del bass-reflex
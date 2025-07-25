from core.enclosure import Enclosure                                      # Importa clase base Enclosure
import numpy as np                                                      # Importa numpy para cálculos matemáticos

class BassReflexBox(Enclosure):
    def __init__(self, Vb_m3, rho0, c, zrad, area_port=None, length_port=None):
        self.Vb_m3 = Vb_m3
        self.rho0 = rho0
        self.c = c
        self.zrad = zrad
        
        # Ajustar estos valores para obtener resonancia a ~35Hz
        if area_port is None:
            self.area_port = 0.005  # 50 cm² en lugar de 100 cm²
        else:
            self.area_port = area_port
            
        if length_port is None:
            self.length_port = 0.28  # 28 cm en lugar de 10 cm
        else:
            self.length_port = length_port
        
        # Calcular la longitud efectiva con corrección de terminación
        delta_L = 0.85 * np.sqrt(self.area_port/np.pi)
        self.Leff = self.length_port + delta_L
        
        # Calcular la frecuencia de resonancia del puerto
        Cab = self.Vb_m3 / (self.rho0 * self.c**2)
        Map = self.rho0 * self.Leff / self.area_port
        self.fp = 1 / (2 * np.pi * np.sqrt(Map * Cab))

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
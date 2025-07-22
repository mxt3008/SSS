from core.enclosure import Enclosure
import numpy as np

class BassReflexBox(Enclosure):
    def __init__(self, vb_litros, area_port, length_port):
        super().__init__(vb_litros)
        self.area_port = area_port  # m²
        self.length_port = length_port  # m

    def acoustic_load(self, f, Sd):
        w = 2 * np.pi * f
        Vb = self.Vb_m3
        S = self.area_port
        L = self.length_port

        delta = 0.85 * np.sqrt(S / np.pi)
        L_eff = L + 2 * delta
        Ma = self.rho0 * L_eff / S
        Ca = Vb / (self.rho0 * self.c**2)
        Za_port = 1j * w * Ma
        Za_box = 1 / (1j * w * Ca)
        Za_total = 1 / (1/Za_port + 1/Za_box)
        Za_mec = Za_total / (Sd**2)
        return Za_mec
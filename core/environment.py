# --------------------------------------------
# environment.py
# Definición rigurosa del entorno acústico. Cada constante se deriva desde principios físicos fundamentales.
# --------------------------------------------

import numpy as np                                                      # Importa numpy para cálculos matemáticos

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

class AcousticEnvironment:

    def __init__(self, T0: float = 293.15, P0: float = 101325.0, gamma: float = 1.4, M: float = 0.02896):
        
        self.R_universal = 8.3145                                       # Constante universal de los gases en J/mol·K

        self.M = M                                                      # Masa molar del aire seco en kg/mol
        self.R = self.R_universal / self.M                              # Constante específica del aire seco R = R_universal / M

        self.T0 = T0                                                    # Temperatura absoluta en K
        self.P0 = P0                                                    # Presión atmosférica en Pa
        self.gamma = gamma                                              # Índice adiabático (Cp/Cv)

        self.rho0 = self.P0 / (self.R * self.T0)                       # Densidad del aire: ρ = P / (R T). Derivada de la ecuación de estado de gas ideal

        self.c = np.sqrt(self.gamma * self.R * self.T0)                # Velocidad del sonido: c = sqrt(γ R T). Derivada de la definición de compresibilidad adiabática

    def resumen(self):
        return f"""
        ===================================================
        PARÁMETROS FÍSICOS DERIVADOS DEL ENTORNO ACÚSTICO
        ===================================================
        Temperatura ambiente       T₀   = {self.T0:.2f} K
        Presión atmosférica        P₀   = {self.P0:.2f} Pa
        Masa molar del aire        M    = {self.M:.5f} kg/mol
        Const. universal de gases  Rₘ   = {self.R_universal:.4f} J/(mol·K)
        Const. específica aire     R    = {self.R:.2f} J/(kg·K)
        Índice adiabático (aire)   γ    = {self.gamma:.2f}

        Densidad del aire seco     ρ₀   = {self.rho0:.3f} kg/m³
        Velocidad del sonido       c    = {self.c:.2f} m/s
        ===================================================
        """                                                             # Retorna resumen formateado de los parámetros del entorno
    
#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

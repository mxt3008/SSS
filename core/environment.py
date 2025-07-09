# --------------------------------------------
# environment.py
# Definición rigurosa del entorno acústico. Cada constante se deriva desde principios físicos fundamentales.
# --------------------------------------------

import numpy as np

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

class AcousticEnvironment:

    def __init__(self, T0: float = 293.15, P0: float = 101325.0, gamma: float = 1.4, M: float = 0.02896):
    #====================================================================================================================================
    # T0    : Temperatura ambiente en Kelvin (default: 293.15 K = 20°C)
    # P0    : Presión atmosférica en Pascales (default: 101325 Pa)
    # gamma : Coeficiente adiabático del aire seco (≈1.4)
    # M     : Masa molar del aire seco en kg/mol (≈28.96 g/mol)
    #====================================================================================================================================

        # ----------------------------------------
        # Constante universal de los gases
        # ----------------------------------------
        self.R_universal = 8.3145                       # [J/mol·K]

        # ----------------------------------------
        # Constante específica del aire seco
        # R = R_universal / M
        # ----------------------------------------
        self.M = M
        self.R = self.R_universal / self.M              # [J/kg·K]

        # ----------------------------------------
        # Parámetros de entrada
        # ----------------------------------------
        self.T0 = T0                                     # Temperatura absoluta [K]
        self.P0 = P0                                     # Presión atmosférica [Pa]
        self.gamma = gamma                               # Índice adiabático (Cp/Cv)

        # ----------------------------------------
        # Densidad del aire: ρ = P / (R T). Derivada de la ecuación de estado de gas ideal.
        # ----------------------------------------
        self.rho0 = self.P0 / (self.R * self.T0)         # [kg/m³]

        # ----------------------------------------
        # Velocidad del sonido: c = sqrt(γ R T). Derivada de la definición de compresibilidad adiabática.
        # ----------------------------------------
        self.c = np.sqrt(self.gamma * self.R * self.T0)  # [m/s]

    # ----------------------------------------
    # Reporte completo
    # ----------------------------------------

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
        """
    
#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

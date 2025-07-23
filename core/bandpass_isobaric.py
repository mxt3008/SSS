import numpy as np

class BandpassIsobaricBox:
    def __init__(self, params):
        # params: diccionario con todos los parámetros necesarios
        self.p = params

    def simulate(self, freq):
        # Extrae parámetros principales
        p = self.p
        fs = p['fs']        # Frecuencia de resonancia del driver
        fp = p['fp']        # Frecuencia de sintonía del puerto
        Qes = p['Qes']      # Factor de calidad eléctrico
        Qms = p['Qms']      # Factor de calidad mecánico
        BL = p['BL']        # Factor motor
        Re = p['Re']        # Resistencia DC
        V0 = p['V0']        # Voltaje de entrada
        S = p['S']          # Área del diafragma

        # Factor de calidad total
        Qts = 1/(1/Qes + 1/Qms)
        
        # === MODELO SIMPLIFICADO BANDPASS ISOBÁRICO ===
        # Tres frecuencias características basadas en teoría de Linkwitz-Small
        f1 = fs * 0.75      # Resonancia baja (driver libre)
        f2 = fp             # Resonancia del puerto (Helmholtz)
        f3 = fs * 1.9       # Resonancia alta (driver en caja cerrada)
        
        # Factores Q optimizados para resonancias visibles
        Q1 = Qts * 1.8      # Q moderado para resonancia baja
        Q2 = 15             # Q alto para resonancia del puerto
        Q3 = Qts * 1.2      # Q moderado para resonancia alta
        
        # Simulación optimizada
        SPL = []
        SPLΦ = []
        Zt = []
        ZtΦ = []
        DEZ = []
        LWA = []
        datos = []
        groupdelay = []

        for freqi in freq:
            w = 2*np.pi*freqi
            s = 1j*w
            
            # === TRES RESONANCIAS RLC ===
            w1, w2, w3 = 2*np.pi*f1, 2*np.pi*f2, 2*np.pi*f3
            
            # Resonancia 1 (driver libre - baja frecuencia)
            Z1_num = Re * Q1**2 * (s/w1)
            Z1_den = 1 + Q1*(s/w1 - w1/s)
            Z1 = Z1_num / (Z1_den + 1e-12)  # Evitar división por cero
            
            # Resonancia 2 (puerto Helmholtz - media frecuencia)  
            Z2_num = Re * Q2**2 * (s/w2)
            Z2_den = 1 + Q2*(s/w2 - w2/s)
            Z2 = Z2_num / (Z2_den + 1e-12)
            
            # Resonancia 3 (driver en caja - alta frecuencia)
            Z3_num = Re * Q3**2 * (s/w3)  
            Z3_den = 1 + Q3*(s/w3 - w3/s)
            Z3 = Z3_num / (Z3_den + 1e-12)
            
            # === COMBINACIÓN CARACTERÍSTICA BANDPASS ===
            # Las resonancias del driver (1 y 3) en paralelo
            Z_driver_parallel = 1/(1/(Z1 + 1e-12) + 1/(Z3 + 1e-12))
            
            # El puerto (resonancia 2) en serie con el conjunto driver
            Z_bandpass = Z2 + Z_driver_parallel
            
            # Impedancia eléctrica total
            Ze_total = Re + Z_bandpass
            
            # Para configuración isobárica: dos drivers en paralelo
            Ze_final = Ze_total / 2
            
            # Magnitud y fase
            Ze_mag = np.abs(Ze_final)
            Ze_phase = np.angle(Ze_final, deg=True)
            
            Zt.append(Ze_mag)
            ZtΦ.append(Ze_phase)
            datos.append(Ze_phase)
            
            # === CÁLCULOS ACÚSTICOS ===
            # SPL basado en transferencia electroacústica
            transfer_factor = V0 / (Ze_mag + Re/2)
            frequency_response = freqi * S * transfer_factor
            SPL_value = 20*np.log10(np.abs(frequency_response * 1000)) + 75
            SPL.append(np.clip(SPL_value, 0, 120))  # Limitar rango realista
            
            # Desplazamiento del cono
            velocity = transfer_factor
            displacement = np.abs(velocity) / (w + 1e-10) * 1000  # mm
            DEZ.append(np.clip(displacement, 0, 50))  # Límite realista
            
            # LWA (placeholder compatible)
            LWA.append(SPL_value)

        # Group delay (diferencial de fase)
        for i in range(1, len(datos)-1):
            if i == 1:
                groupdelay.append(0)  # Primer punto
            groupdelay_val = -1000*((datos[i] - datos[i-1])/(freq[i] - freq[i-1]) + 
                                   (datos[i+1] - datos[i])/(freq[i+1] - freq[i]))/(2*360)
            groupdelay.append(groupdelay_val)
        
        if len(groupdelay) < len(freq):
            groupdelay.append(groupdelay[-1] if groupdelay else 0)  # Último punto

        return {
            "freq": freq,
            "Zt": np.array(Zt),
            "ZtΦ": np.array(ZtΦ),
            "SPL": np.array(SPL),
            "DEZ": np.array(DEZ),
            "groupdelay": np.array(groupdelay),
            "LWA": np.array(LWA),
        }
    
    def total_acoustic_load(self, f, Sd):
        """
        Método de compatibilidad con la clase Driver.
        Devuelve la impedancia acústica total vista por el driver.
        """
        # Simplificación: devolver impedancia acústica basada en los cálculos internos
        # Para una implementación más completa, esto debería usar los cálculos 
        # de impedancia del sistema bandpass isobárico
        
        # Por ahora, usar una aproximación basada en los parámetros de la caja trasera
        w = 2 * np.pi * f
        p = self.p
        
        # Impedancia acústica básica de la cámara trasera
        ρ0 = p['rho0']
        c0 = p['c0']
        Vab = p['Vab']
        
        # Reactancia acústica de la cámara trasera
        Ca = Vab / (ρ0 * c0**2)  # Compliance acústica
        Za = 1 / (1j * w * Ca)   # Impedancia acústica
        
        return Za
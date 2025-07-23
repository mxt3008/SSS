#!/usr/bin/env python3
# Modelo de referencia para bandpass isobárico con circuito clásico

import numpy as np
import matplotlib.pyplot as plt

class BandpassIsobaricReference:
    """Modelo de referencia basado en la literatura de Linkwitz y Small"""
    
    def __init__(self, params):
        self.p = params
        
    def simulate(self, freq):
        p = self.p
        
        # Parámetros básicos
        fs = p['fs']
        Qes = p['Qes'] 
        Qms = p['Qms']
        BL = p['BL']
        Re = p['Re']
        S = p['S']
        Vab = p['Vab']  # Cámara trasera
        fp = p['fp']    # Sintonía del puerto
        
        # Parámetros derivados
        w_s = 2*np.pi*fs
        Mms = Qes*(BL**2)/(w_s*Re)
        Cms = 1/(Mms*w_s**2)
        Rms = w_s*Mms/Qms
        
        # Compliance de la cámara trasera
        rho0 = p['rho0']
        c0 = p['c0']
        Cab = Vab/(rho0*c0**2)
        
        # Masa del puerto
        Lp_eff = p['Lp'] + 0.85*p['dp']  # Longitud efectiva con corrección
        Map = rho0*Lp_eff/(np.pi*(p['dp']/2)**2)
        
        # Resistencia del puerto (pérdidas)
        Rap = 1.0  # Resistencia nominal del puerto
        
        # Simulación
        Zt = []
        SPL = []
        ZtPhi = []
        DEZ = []
        
        for f in freq:
            w = 2*np.pi*f
            s = 1j*w  # Variable de Laplace
            
            # Impedancias mecánicas del driver
            Zms = Rms + s*Mms + 1/(s*Cms)
            
            # Impedancia de la cámara trasera
            Zcab = 1/(s*Cab)
            
            # Impedancia del puerto
            Zmap = Rap + s*Map
            
            # Circuito equivalente bandpass isobárico
            # El driver ve en paralelo: la cámara trasera y el puerto
            Zmech_load = 1/(1/Zcab + 1/Zmap)
            
            # Impedancia mecánica total
            Zmech_total = Zms + Zmech_load
            
            # Impedancia eléctrica vista desde los terminales
            Ze = Re + (BL**2)/Zmech_total
            
            # Corrección para isobárico (dos drivers en paralelo eléctricamente)
            Ze = Ze/2
            
            # Magnitud y fase
            Ze_mag = np.abs(Ze)
            Ze_phase = np.angle(Ze, deg=True)
            
            Zt.append(Ze_mag)
            ZtPhi.append(Ze_phase)
            
            # SPL simplificado
            # Velocidad del diafragma
            vel = (BL*p['V0'])/(BL**2 + Ze*Zmech_total)
            
            # Presión acústica (simplificada)
            pressure = (rho0*c0*S*vel)/(4*np.pi*1)  # A 1 metro
            spl = 20*np.log10(np.abs(pressure)/20e-6)
            SPL.append(spl)
            
            # Desplazamiento
            disp = np.abs(vel)/(w) * 1000  # mm
            DEZ.append(disp)
        
        return {
            "freq": freq,
            "Zt": np.array(Zt),
            "ZtΦ": np.array(ZtPhi), 
            "SPL": np.array(SPL),
            "DEZ": np.array(DEZ),
            "groupdelay": np.zeros_like(freq),  # Placeholder
            "LWA": np.array(SPL),  # Placeholder
        }

# Test del modelo de referencia
if __name__ == "__main__":
    print("=== MODELO DE REFERENCIA BANDPASS ISOBÁRICO ===")
    
    # Parámetros optimizados
    params = {
        'rho0': 1.2, 'c0': 344, 'BL': 18.1, 'Re': 5.3, 'Red': 3.77,
        'Qes': 0.34, 'Qms': 4.5, 'fs': 52, 'Lvc': 0.1, 'S': 0.055,
        'Vab': 0.030, 'Vf': 0.010, 'fp': 65, 'dd': 0.20, 'dp': 0.08, 
        'Lp': 0.12, 'B': 0.8333, 'Mmd': 0.015, 'V0': 2.83,
    }
    
    # Simulación
    frequencies = np.logspace(np.log10(10), np.log10(200), 1000)
    
    # Modelo original
    from core.bandpass_isobaric import BandpassIsobaricBox
    bandpass_orig = BandpassIsobaricBox(params)
    results_orig = bandpass_orig.simulate(frequencies)
    
    # Modelo de referencia
    bandpass_ref = BandpassIsobaricReference(params)
    results_ref = bandpass_ref.simulate(frequencies)
    
    # Detectar picos en ambos
    from scipy.signal import find_peaks
    
    peaks_orig, _ = find_peaks(results_orig["Zt"], height=np.max(results_orig["Zt"])*0.05, distance=30)
    peaks_ref, _ = find_peaks(results_ref["Zt"], height=np.max(results_ref["Zt"])*0.05, distance=30)
    
    print(f"Modelo original: {len(peaks_orig)} picos")
    print(f"Modelo referencia: {len(peaks_ref)} picos")
    
    # Comparación gráfica
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.semilogx(frequencies, results_orig["Zt"], 'b-', label='Modelo Original')
    plt.plot(frequencies[peaks_orig], results_orig["Zt"][peaks_orig], 'bo', markersize=8)
    plt.grid(True, alpha=0.3)
    plt.xlabel('Frecuencia [Hz]')
    plt.ylabel('Impedancia [Ω]')
    plt.title(f'Original ({len(peaks_orig)} picos)')
    plt.legend()
    
    plt.subplot(1, 3, 2)
    plt.semilogx(frequencies, results_ref["Zt"], 'r-', label='Modelo Referencia')
    plt.plot(frequencies[peaks_ref], results_ref["Zt"][peaks_ref], 'ro', markersize=8)
    plt.grid(True, alpha=0.3)
    plt.xlabel('Frecuencia [Hz]')
    plt.ylabel('Impedancia [Ω]')
    plt.title(f'Referencia ({len(peaks_ref)} picos)')
    plt.legend()
    
    plt.subplot(1, 3, 3)
    plt.semilogx(frequencies, results_orig["Zt"], 'b-', label='Original')
    plt.semilogx(frequencies, results_ref["Zt"], 'r--', label='Referencia')
    plt.grid(True, alpha=0.3)
    plt.xlabel('Frecuencia [Hz]')
    plt.ylabel('Impedancia [Ω]')
    plt.title('Comparación')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('comparacion_modelos.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print("Comparación guardada como 'comparacion_modelos.png'")

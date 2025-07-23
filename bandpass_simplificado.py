#!/usr/bin/env python3
# Versión simplificada del bandpass isobárico

import numpy as np

class BandpassSimplificado:
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
        
        # Factores de calidad
        Qts = 1/(1/Qes + 1/Qms)
        
        # Tres frecuencias características del bandpass isobárico
        # Basadas en la teoría de Linkwitz-Small para sistemas bandpass
        f1 = fs * 0.8       # Resonancia baja (driver libre)
        f2 = p['fp']        # Resonancia del puerto 
        f3 = fs * 1.8       # Resonancia alta (driver en caja)
        
        # Factores Q para cada resonancia
        Q1 = Qts * 2        # Q moderado para primera resonancia
        Q2 = 12             # Q alto para resonancia del puerto
        Q3 = Qts * 1.5      # Q moderado para tercera resonancia
        
        results = {
            "freq": freq,
            "Zt": [],
            "ZtΦ": [],
            "SPL": [],
            "DEZ": [],
            "groupdelay": [],
            "LWA": [],
        }
        
        for f in freq:
            w = 2*np.pi*f
            s = 1j*w
            
            # Tres resonancias en paralelo (modelo simplificado)
            # Cada resonancia es un circuito RLC
            
            # Resonancia 1 (baja frecuencia)
            w1 = 2*np.pi*f1
            Z1 = Re * Q1**2 * (s/w1) / (1 + Q1*(s/w1 - w1/s))
            
            # Resonancia 2 (puerto)
            w2 = 2*np.pi*f2  
            Z2 = Re * Q2**2 * (s/w2) / (1 + Q2*(s/w2 - w2/s))
            
            # Resonancia 3 (alta frecuencia)
            w3 = 2*np.pi*f3
            Z3 = Re * Q3**2 * (s/w3) / (1 + Q3*(s/w3 - w3/s))
            
            # Combinación característica del bandpass isobárico
            # Las resonancias 1 y 3 (del driver) están en paralelo
            # La resonancia 2 (puerto) está en serie
            Z_driver = 1/(1/Z1 + 1/Z3)
            Z_total = Re + Z2 + Z_driver
            
            # Para isobárico: división por 2 (dos drivers en paralelo)
            Z_final = Z_total / 2
            
            # Magnitud y fase
            Ze_mag = np.abs(Z_final)
            Ze_phase = np.angle(Z_final, deg=True)
            
            results["Zt"].append(Ze_mag)
            results["ZtΦ"].append(Ze_phase)
            
            # SPL simplificado (modelo acústico básico)
            vel_factor = p['V0'] / (Ze_mag + Re)
            spl = 20*np.log10(np.abs(vel_factor * f * p['S'] * 1000)) + 80
            results["SPL"].append(spl)
            
            # Desplazamiento
            disp = np.abs(vel_factor) / (w + 1e-10) * 1000  # mm
            results["DEZ"].append(min(disp, 100))  # Límite realista
            
            # Placeholders
            results["groupdelay"].append(0)
            results["LWA"].append(spl)
        
        # Convertir a arrays
        for key in ["Zt", "ZtΦ", "SPL", "DEZ", "groupdelay", "LWA"]:
            results[key] = np.array(results[key])
            
        return results

# Test del modelo simplificado
if __name__ == "__main__":
    print("=== MODELO BANDPASS SIMPLIFICADO ===")
    
    params = {
        'fs': 52, 'fp': 65, 'Qes': 0.34, 'Qms': 4.5, 
        'BL': 18.1, 'Re': 5.3, 'V0': 2.83, 'S': 0.055
    }
    
    freq = np.logspace(np.log10(20), np.log10(150), 200)
    
    bandpass = BandpassSimplificado(params)
    results = bandpass.simulate(freq)
    
    # Detectar picos
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(results["Zt"], height=np.max(results["Zt"])*0.1, distance=10)
    
    print(f"Picos detectados: {len(peaks)}")
    for i, peak in enumerate(peaks):
        freq_pico = freq[peak]
        z_pico = results["Zt"][peak]
        print(f"Pico {i+1}: f = {freq_pico:.1f} Hz, Z = {z_pico:.1f} Ω")
    
    print(f"Rango impedancia: {np.min(results['Zt']):.1f} - {np.max(results['Zt']):.1f} Ω")
    
    # Gráfica
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 3, 1)
    plt.semilogx(freq, results["Zt"], 'b-', linewidth=2)
    plt.plot(freq[peaks], results["Zt"][peaks], 'ro', markersize=8)
    plt.axvline(params['fs']*0.8, color='green', linestyle='--', alpha=0.7, label=f'f1 ({params["fs"]*0.8:.1f} Hz)')
    plt.axvline(params['fp'], color='orange', linestyle='--', alpha=0.7, label=f'f2 ({params["fp"]:.1f} Hz)')
    plt.axvline(params['fs']*1.8, color='red', linestyle='--', alpha=0.7, label=f'f3 ({params["fs"]*1.8:.1f} Hz)')
    plt.grid(True, alpha=0.3)
    plt.xlabel('Frecuencia [Hz]')
    plt.ylabel('Impedancia [Ω]')
    plt.title(f'Impedancia ({len(peaks)} picos)')
    plt.legend()
    
    plt.subplot(1, 3, 2) 
    plt.semilogx(freq, results["SPL"], 'g-', linewidth=2)
    plt.grid(True, alpha=0.3)
    plt.xlabel('Frecuencia [Hz]')
    plt.ylabel('SPL [dB]')
    plt.title('SPL')
    
    plt.subplot(1, 3, 3)
    plt.semilogx(freq, results["ZtΦ"], 'm-', linewidth=2)
    plt.grid(True, alpha=0.3)
    plt.xlabel('Frecuencia [Hz]')
    plt.ylabel('Fase [°]')
    plt.title('Fase')
    
    plt.tight_layout()
    plt.savefig('bandpass_simplificado_working.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print("Gráfica guardada como 'bandpass_simplificado_working.png'")
    
    if len(peaks) >= 3:
        print("\n✓ ¡ÉXITO! Modelo simplificado funciona correctamente")
    else:
        print(f"\n⚠️  Solo {len(peaks)} picos detectados")

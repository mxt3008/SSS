#!/usr/bin/env python3
"""
Verificación final del modelo bass-reflex vs VituixCAD
"""

import numpy as np
import matplotlib.pyplot as plt
from core.driver import Driver
from core.bassreflex import BassReflexBox

def test_final_verification():
    print("🎯 VERIFICACIÓN FINAL BASS-REFLEX vs VITUIXCAD")
    
    # Parámetros del driver Peerless SLS-P830946
    driver_params = {
        "Fs": 37.5,      # Hz - frecuencia de resonancia
        "Qts": 0.38,     # factor de calidad total
        "Qes": 0.42,     # factor de calidad eléctrico  
        "Qms": 3.1,      # factor de calidad mecánico
        "Vas": 18.5,     # litros - volumen de aire equivalente
        "Re": 5.4,       # ohm - resistencia DC
        "Mms": 21.0e-3,  # kg - masa del cono
        "Cms": 1.8e-3,   # m/N - compliance
        "Rms": 2.8,      # resistencia mecánica
        "Sd": 0.0177,    # m^2 - área efectiva del cono
        "Bl": 7.5,       # Tm - factor de fuerza
        "Xmax": 4.5e-3   # m - excursión máxima
    }
    driver = Driver(driver_params)
    
    # Configuración bass-reflex
    enclosure = BassReflexBox(
        vb_litros=25.0,      # litros
        area_port=0.0031,    # m^2
        length_port=0.15     # m - longitud del puerto
    )
    
    # Frecuencias de prueba
    frequencies = np.logspace(np.log10(10), np.log10(200), 200)
    
    print("\n🔍 CALCULANDO IMPEDANCIA...")
    impedance = []
    for f in frequencies:
        Z = driver.impedance(f, enclosure)
        impedance.append(Z)
    
    # Encontrar picos de impedancia
    impedance = np.array(impedance)
    peaks = []
    for i in range(1, len(impedance)-1):
        if impedance[i] > impedance[i-1] and impedance[i] > impedance[i+1]:
            if impedance[i] > 30:  # Solo picos significativos
                peaks.append((frequencies[i], impedance[i]))
    
    print(f"Picos encontrados:")
    for freq, imp in peaks:
        print(f"  {freq:.1f} Hz @ {imp:.1f} Ω")
    
    print("\n🔍 CALCULANDO SPL...")
    spl_cone = []
    spl_port = []
    spl_total = []
    
    for f in frequencies:
        cone = driver.spl_bassreflex_cone(f, enclosure)
        port = driver.spl_bassreflex_port(f, enclosure)
        total = driver.spl_bassreflex_total(f, enclosure)
        
        spl_cone.append(cone)
        spl_port.append(port)
        spl_total.append(total)
    
    # Rangos de SPL
    print(f"SPL Cono: {min(spl_cone):.1f} - {max(spl_cone):.1f} dB")
    print(f"SPL Puerto: {min(spl_port):.1f} - {max(spl_port):.1f} dB")
    print(f"SPL Total: {min(spl_total):.1f} - {max(spl_total):.1f} dB")
    
    # Crear gráfico final
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Gráfico de impedancia
    ax1.semilogx(frequencies, impedance, 'k-', linewidth=2, label='Impedancia')
    ax1.set_xlabel('Frecuencia (Hz)')
    ax1.set_ylabel('Impedancia (Ω)')
    ax1.set_title('IMPEDANCIA BASS-REFLEX vs VITUIXCAD')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_xlim(10, 200)
    ax1.set_ylim(0, 70)
    
    # Marcar picos esperados
    ax1.axvline(22, color='red', linestyle='--', alpha=0.7, label='VituixCAD: 22Hz@58Ω')
    ax1.axvline(92, color='red', linestyle='--', alpha=0.7, label='VituixCAD: 92Hz@64Ω')
    ax1.axhline(58, color='red', linestyle='--', alpha=0.7)
    ax1.axhline(64, color='red', linestyle='--', alpha=0.7)
    
    # Gráfico de SPL
    ax2.semilogx(frequencies, spl_cone, 'b-', linewidth=2, label='SPL Cono')
    ax2.semilogx(frequencies, spl_port, 'r-', linewidth=2, label='SPL Puerto')
    ax2.semilogx(frequencies, spl_total, 'c-', linewidth=2, label='SPL Total')
    ax2.set_xlabel('Frecuencia (Hz)')
    ax2.set_ylabel('SPL (dB)')
    ax2.set_title('SPL BASS-REFLEX vs VITUIXCAD')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_xlim(10, 200)
    
    plt.tight_layout()
    plt.savefig('outputs/verificacion_final.png', dpi=300, bbox_inches='tight')
    print(f"\n📊 Gráfica guardada: outputs/verificacion_final.png")
    
    print("\n✅ VERIFICACIÓN COMPLETADA")
    print("🎯 Comparar con VituixCAD:")
    print("   - Impedancia: dos picos ~22Hz@58Ω y ~92Hz@64Ω")
    print("   - SPL: cono (azul) declina, puerto (rojo) pico ~50Hz, total (turquesa) combinado")

if __name__ == "__main__":
    test_final_verification()

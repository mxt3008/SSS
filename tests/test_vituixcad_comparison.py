"""
Test para comparar con VituixCAD - Impedancia y SPL con contribuciones separadas
"""

import numpy as np
import matplotlib.pyplot as plt
from core.driver import Driver
from core.bassreflex import BassReflexBox

def test_vituixcad_comparison():
    print("🎯 COMPARACIÓN CON VITUIXCAD")
    
    # Parámetros del driver (similares a VituixCAD)
    params = {
        'Fs': 52,      # Hz - Frecuencia de resonancia
        'Qts': 0.35,   # Factor de calidad total
        'Qes': 0.4,    # Factor de calidad eléctrico
        'Re': 6.5,     # Ohm - Resistencia DC
        'Sd': 0.0133,  # m² - Área efectiva del diafragma
        'Vas': 15,     # litros - Volumen de aire equivalente
        'Xmax': 0.004, # m - Excursión máxima lineal
        'Bl': 5.5,     # T⋅m - Factor de fuerza
        'Le': 0.4e-3,  # H - Inductancia de la bobina
        'Rg': 0,       # Ohm - Resistencia del generador
        'Mms': 0.01,   # kg - Masa del diafragma
        'Cms': 1.8e-3, # m/N - Compliancia mecánica
    }
    
    # Caja bass-reflex similar a VituixCAD  
    enclosure = BassReflexBox(
        vb_litros=20,           # litros
        area_port=0.001,        # m² - área del puerto
        length_port=0.05        # m - longitud del puerto
    )
    
    # Driver con caja bass-reflex
    driver = Driver(params, enclosure)
    driver.resumen_parametros()
    
    # Rango de frecuencias
    f = np.logspace(1, 3, 1000)  # 10 Hz a 1 kHz
    
    # === IMPEDANCIA ===
    Z = driver.impedance(f)
    Z_mag = np.abs(Z)
    Z_phase = np.angle(Z, deg=True)
    
    # Buscar picos
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(Z_mag, height=50, distance=50)
    
    print(f"\n🔍 ANÁLISIS DE IMPEDANCIA:")
    print(f"Rango: {Z_mag.min():.1f} - {Z_mag.max():.1f} Ω")
    if len(peaks) >= 2:
        print(f"Pico 1: {f[peaks[0]]:.1f} Hz, {Z_mag[peaks[0]]:.1f} Ω")
        print(f"Pico 2: {f[peaks[1]]:.1f} Hz, {Z_mag[peaks[1]]:.1f} Ω")
    
    # === SPL SEPARADO ===
    spl_total = driver.spl_total(f)
    spl_cone = driver.spl_bassreflex_cone(f)
    spl_port = driver.spl_bassreflex_port(f)
    
    print(f"\n🔍 ANÁLISIS DE SPL:")
    print(f"SPL Total rango: {spl_total.min():.1f} - {spl_total.max():.1f} dB")
    print(f"SPL Cono rango: {spl_cone.min():.1f} - {spl_cone.max():.1f} dB")
    print(f"SPL Puerto rango: {spl_port.min():.1f} - {spl_port.max():.1f} dB")
    
    # === GRÁFICAS ===
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # Impedancia - Magnitud
    ax1.semilogx(f, Z_mag, 'b-', linewidth=2, label='|Z|')
    ax1.set_xlabel('Frecuencia [Hz]')
    ax1.set_ylabel('Impedancia [Ω]')
    ax1.set_title('Impedancia - Magnitud (como VituixCAD)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_ylim(0, 100)
    
    # Marcar picos
    if len(peaks) >= 2:
        ax1.plot(f[peaks[:2]], Z_mag[peaks[:2]], 'ro', markersize=8)
        for i, peak in enumerate(peaks[:2]):
            ax1.annotate(f'Pico {i+1}\n{f[peak]:.1f} Hz\n{Z_mag[peak]:.1f} Ω',
                        xy=(f[peak], Z_mag[peak]), xytext=(10, 10),
                        textcoords='offset points', fontsize=9,
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    # Impedancia - Fase
    ax2.semilogx(f, Z_phase, 'r-', linewidth=2, label='Fase')
    ax2.set_xlabel('Frecuencia [Hz]')
    ax2.set_ylabel('Fase [°]')
    ax2.set_title('Impedancia - Fase')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # SPL - Magnitud (como VituixCAD)
    ax3.semilogx(f, spl_cone, 'b-', linewidth=2, label='Cono (azul)')
    ax3.semilogx(f, spl_port, 'r-', linewidth=2, label='Puerto (rojo)')
    ax3.semilogx(f, spl_total, 'c-', linewidth=3, label='Total (turquesa)')
    ax3.set_xlabel('Frecuencia [Hz]')
    ax3.set_ylabel('SPL [dB]')
    ax3.set_title('SPL - Cono + Puerto + Total (como VituixCAD)')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    ax3.set_ylim(40, 110)
    
    # SPL - Fase
    spl_phase_total = np.angle(driver.spl_total(f), deg=True)
    ax4.semilogx(f, spl_phase_total, 'g-', linewidth=2, label='Fase SPL')
    ax4.set_xlabel('Frecuencia [Hz]')
    ax4.set_ylabel('Fase [°]')
    ax4.set_title('SPL - Fase')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig('outputs/comparacion_vituixcad.png', dpi=300, bbox_inches='tight')
    print(f"\n📊 Gráfica guardada: outputs/comparacion_vituixcad.png")
    print(f"🎯 Comparar con VituixCAD:")
    print(f"   - Impedancia: dos picos ~20Hz y ~70Hz, valle ~50Hz")
    print(f"   - SPL: cono (azul) + puerto (rojo) = total (turquesa)")

if __name__ == "__main__":
    test_vituixcad_comparison()

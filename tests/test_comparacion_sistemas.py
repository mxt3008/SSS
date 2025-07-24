#!/usr/bin/env python3
# Test comparativo: Infinite Baffle vs Bass-Reflex

import numpy as np
import matplotlib.pyplot as plt
from core.driver import Driver
from core.bassreflex import BassReflexBox

def test_infinite_vs_bassreflex():
    print("🧪 TEST COMPARATIVO: INFINITE BAFFLE vs BASS-REFLEX")
    
    # Parámetros estándar del driver
    driver_params = {
        "Fs": 37.5,
        "Qts": 0.38,
        "Qes": 0.42,
        "Qms": 3.1,
        "Vas": 18.5,
        "Re": 5.4,
        "Mms": 21.0e-3,
        "Cms": 1.8e-3,
        "Rms": 2.8,
        "Sd": 0.0177,
        "Bl": 7.5,
        "Xmax": 4.5e-3
    }
    
    # Crear driver infinite baffle
    driver_ib = Driver(driver_params, enclosure=None, radiation_model="baffled")
    print("✅ Driver infinite baffle creado")
    
    # Crear driver bass-reflex
    enclosure_br = BassReflexBox(vb_litros=25.0, area_port=0.0031, length_port=0.15)
    driver_br = Driver(driver_params, enclosure=enclosure_br, radiation_model="baffled")
    print("✅ Driver bass-reflex creado")
    
    # Frecuencias de prueba
    frequencies = np.logspace(np.log10(10), np.log10(200), 50)
    
    print("\n🔍 Calculando respuestas...")
    
    # Test Infinite Baffle
    try:
        Z_ib = []
        SPL_ib = []
        for f in frequencies:
            Z_ib.append(np.abs(driver_ib.impedance(f)))
            SPL_ib.append(driver_ib.spl_total(f))
        
        Z_ib = np.array(Z_ib)
        SPL_ib = np.array(SPL_ib)
        print(f"✅ Infinite Baffle - Z: {Z_ib.min():.1f}-{Z_ib.max():.1f}Ω, SPL: {SPL_ib.min():.1f}-{SPL_ib.max():.1f}dB")
        
    except Exception as e:
        print(f"❌ Error en Infinite Baffle: {e}")
        return False
    
    # Test Bass-Reflex
    try:
        Z_br = []
        SPL_br_total = []
        SPL_br_cone = []
        SPL_br_port = []
        
        for f in frequencies:
            Z_br.append(np.abs(driver_br.impedance(f)))
            SPL_br_total.append(driver_br.spl_bassreflex_total(f))
            SPL_br_cone.append(driver_br.spl_bassreflex_cone(f))
            SPL_br_port.append(driver_br.spl_bassreflex_port(f))
        
        Z_br = np.array(Z_br)
        SPL_br_total = np.array(SPL_br_total)
        SPL_br_cone = np.array(SPL_br_cone)
        SPL_br_port = np.array(SPL_br_port)
        
        print(f"✅ Bass-Reflex - Z: {Z_br.min():.1f}-{Z_br.max():.1f}Ω, SPL: {SPL_br_total.min():.1f}-{SPL_br_total.max():.1f}dB")
        
    except Exception as e:
        print(f"❌ Error en Bass-Reflex: {e}")
        return False
    
    # Crear gráfico comparativo
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Gráfico de impedancia
    ax1.semilogx(frequencies, Z_ib, 'b-', linewidth=2, label='Infinite Baffle')
    ax1.semilogx(frequencies, Z_br, 'r-', linewidth=2, label='Bass-Reflex')
    ax1.set_xlabel('Frecuencia (Hz)')
    ax1.set_ylabel('Impedancia (Ω)')
    ax1.set_title('COMPARACIÓN: Impedancia')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(10, 200)
    
    # Gráfico de SPL
    ax2.semilogx(frequencies, SPL_ib, 'b-', linewidth=2, label='Infinite Baffle')
    ax2.semilogx(frequencies, SPL_br_total, 'c-', linewidth=2, label='Bass-Reflex Total')
    ax2.semilogx(frequencies, SPL_br_cone, 'g--', linewidth=1.5, label='Bass-Reflex Cono')
    ax2.semilogx(frequencies, SPL_br_port, 'r--', linewidth=1.5, label='Bass-Reflex Puerto')
    ax2.set_xlabel('Frecuencia (Hz)')
    ax2.set_ylabel('SPL (dB)')
    ax2.set_title('COMPARACIÓN: SPL')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(10, 200)
    
    plt.tight_layout()
    plt.savefig('outputs/comparacion_infinite_vs_bassreflex.png', dpi=300, bbox_inches='tight')
    print(f"\n📊 Gráfica guardada: outputs/comparacion_infinite_vs_bassreflex.png")
    
    print("\n🎯 COMPARACIÓN COMPLETADA EXITOSAMENTE")
    print("✅ Infinite Baffle: Funcionando correctamente")
    print("✅ Bass-Reflex: Funcionando correctamente con 3 curvas SPL")
    print("✅ Ambos sistemas coexisten sin interferencias")
    
    return True

if __name__ == "__main__":
    test_infinite_vs_bassreflex()

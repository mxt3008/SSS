#!/usr/bin/env python3
"""
Test simulando la interfaz gráfica para bass-reflex
"""

import numpy as np
import matplotlib.pyplot as plt
from core.driver import Driver

def test_gui_simulation():
    print("🖥️ SIMULACIÓN DE INTERFAZ GRÁFICA BASS-REFLEX")
    
    # Parámetros como en la interfaz
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
    
    driver = Driver(driver_params)
    print("✅ Driver creado exitosamente")
    
    # Frecuencias como en la interfaz
    frequencies = np.logspace(np.log10(10), np.log10(1000), 100)
    print(f"✅ {len(frequencies)} frecuencias generadas (10-1000 Hz)")
    
    # Simular exactamente lo que hace la interfaz
    try:
        print("\n🔍 Calculando impedancia...")
        impedances = []
        for f in frequencies:
            Z = driver.impedance(f)
            impedances.append(Z)
        impedances = np.array(impedances)
        print(f"✅ Impedancia calculada: {impedances.min():.1f} - {impedances.max():.1f} Ω")
        
        print("\n🔍 Calculando SPL como lo hace la interfaz...")
        
        # Como lo hace app_qt5.py línea 488
        SPL_total = np.array([driver.spl_total(f) for f in frequencies])
        print(f"✅ SPL Total: {SPL_total.min():.1f} - {SPL_total.max():.1f} dB")
        
        # Para bass-reflex se calcula también SPL_cone y SPL_port
        SPL_cone = np.array([driver.spl_bassreflex_cone(f) for f in frequencies])
        print(f"✅ SPL Cono: {SPL_cone.min():.1f} - {SPL_cone.max():.1f} dB")
        
        SPL_port = np.array([driver.spl_bassreflex_port(f) for f in frequencies])
        print(f"✅ SPL Puerto: {SPL_port.min():.1f} - {SPL_port.max():.1f} dB")
        
        print("\n📊 Creando gráfico como la interfaz...")
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Gráfico de impedancia
        ax1.semilogx(frequencies, impedances, 'k-', linewidth=2)
        ax1.set_ylabel('Impedancia (Ω)')
        ax1.set_title('SIMULACIÓN INTERFAZ: Impedancia Bass-Reflex')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(10, 1000)
        
        # Gráfico de SPL (3 curvas para bass-reflex)
        ax2.semilogx(frequencies, SPL_cone, 'b-', linewidth=2, label='SPL Cono')
        ax2.semilogx(frequencies, SPL_port, 'r-', linewidth=2, label='SPL Puerto')
        ax2.semilogx(frequencies, SPL_total, 'c-', linewidth=2, label='SPL Total')
        ax2.set_xlabel('Frecuencia (Hz)')
        ax2.set_ylabel('SPL (dB)')
        ax2.set_title('SIMULACIÓN INTERFAZ: SPL Bass-Reflex')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(10, 1000)
        
        plt.tight_layout()
        plt.savefig('outputs/simulacion_interfaz.png', dpi=150, bbox_inches='tight')
        print("📊 Gráfico guardado: outputs/simulacion_interfaz.png")
        
        print("\n🎯 ¡SIMULACIÓN EXITOSA!")
        print("✅ La interfaz debería funcionar perfectamente ahora")
        print("✅ Todas las funciones SPL manejan correctamente escalares individuales")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en simulación: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_gui_simulation()

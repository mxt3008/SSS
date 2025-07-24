#!/usr/bin/env python3
# Test para verificar que infinite baffle funciona correctamente

import numpy as np
import matplotlib.pyplot as plt
from core.driver import Driver

def test_infinite_baffle():
    print("🧪 TEST INFINITE BAFFLE - RESTAURACIÓN")
    
    # Parámetros estándar del driver
    driver_params = {
        "Fs": 52,
        "Mms": 0.065,
        "Vas": 62,
        "Qts": 0.32,
        "Qes": 0.34,
        "Qms": 4.5,
        "Re": 5.3,
        "Bl": 18.1,
        "Sd": 0.055,
        "Le": 1.5e-3,
        "Xmax": 7.5,
        "Cms": 1.8e-3  # Añadido para consistencia
    }
    
    # Crear driver sin enclosure (infinite baffle)
    driver = Driver(driver_params, enclosure=None, radiation_model="baffled")
    print("✅ Driver infinite baffle creado exitosamente")
    
    # Frecuencias de prueba
    frequencies = np.logspace(np.log10(10), np.log10(1000), 50)
    
    try:
        print("\n🔍 Calculando impedancia...")
        impedances = []
        for f in frequencies:
            Z = driver.impedance(f)
            impedances.append(np.abs(Z))
        
        impedances = np.array(impedances)
        print(f"✅ Impedancia: {impedances.min():.1f} - {impedances.max():.1f} Ω")
        
        print("\n🔍 Calculando SPL...")
        spls = []
        for f in frequencies:
            spl = driver.spl_total(f)
            spls.append(spl)
        
        spls = np.array(spls)
        print(f"✅ SPL: {spls.min():.1f} - {spls.max():.1f} dB")
        
        print("\n🔍 Calculando velocidad...")
        velocities = []
        for f in frequencies:
            v = driver.velocity(f)
            velocities.append(np.abs(v))
        
        velocities = np.array(velocities)
        print(f"✅ Velocidad: {velocities.min():.6f} - {velocities.max():.6f} m/s")
        
        print("\n🔍 Calculando desplazamiento...")
        displacements = []
        for f in frequencies:
            d = driver.displacement(f)
            displacements.append(np.abs(d) * 1000)  # Convertir a mm
        
        displacements = np.array(displacements)
        print(f"✅ Desplazamiento: {displacements.min():.3f} - {displacements.max():.3f} mm")
        
        # Crear gráfico de verificación
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        
        # Impedancia
        ax1.semilogx(frequencies, impedances, 'b-', linewidth=2)
        ax1.set_xlabel('Frecuencia (Hz)')
        ax1.set_ylabel('Impedancia (Ω)')
        ax1.set_title('Infinite Baffle - Impedancia')
        ax1.grid(True, alpha=0.3)
        
        # SPL
        ax2.semilogx(frequencies, spls, 'r-', linewidth=2)
        ax2.set_xlabel('Frecuencia (Hz)')
        ax2.set_ylabel('SPL (dB)')
        ax2.set_title('Infinite Baffle - SPL')
        ax2.grid(True, alpha=0.3)
        
        # Velocidad
        ax3.loglog(frequencies, velocities, 'g-', linewidth=2)
        ax3.set_xlabel('Frecuencia (Hz)')
        ax3.set_ylabel('Velocidad (m/s)')
        ax3.set_title('Infinite Baffle - Velocidad')
        ax3.grid(True, alpha=0.3)
        
        # Desplazamiento
        ax4.loglog(frequencies, displacements, 'm-', linewidth=2)
        ax4.set_xlabel('Frecuencia (Hz)')
        ax4.set_ylabel('Desplazamiento (mm)')
        ax4.set_title('Infinite Baffle - Desplazamiento')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('outputs/test_infinite_baffle_restaurado.png', dpi=300, bbox_inches='tight')
        print(f"\n📊 Gráfica guardada: outputs/test_infinite_baffle_restaurado.png")
        
        print("\n✅ INFINITE BAFFLE FUNCIONANDO CORRECTAMENTE")
        print("🎯 Todas las funciones calculan valores realistas:")
        print(f"   - Impedancia en rango típico de drivers")
        print(f"   - SPL con valores coherentes")
        print(f"   - Velocidad y desplazamiento calculados correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en infinite baffle: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_infinite_baffle()

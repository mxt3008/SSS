# test_infinite_baffle_original.py
# Test para verificar que el infinite baffle funciona como originalmente (un solo pico)

import numpy as np
import matplotlib.pyplot as plt
from core.driver import Driver

# Parámetros del driver
driver_params = {
    "Fs": 40,
    "Qts": 0.35,
    "Qes": 0.4,
    "Vas": 50,
    "Sd": 0.02,
    "Re": 6.0,
    "Le": 0.5e-3,
    "Bl": 7.5,
    "Rg": 0.5,
    "Mms": 0.02,    # Masa móvil en kg
    "Cms": 0.001    # Compliancia mecánica en m/N
}

# Crear driver sin enclosure (infinite baffle)
driver = Driver(driver_params, enclosure=None)

# Frecuencias de prueba
f = np.logspace(1, 4, 1000)  # 10 Hz a 10 kHz

try:
    # Calcular impedancia
    Z = driver.impedance(f)
    Z_mag = np.abs(Z)
    
    # Calcular SPL
    spl = driver.spl_total(f, U=2.83)
    
    # Crear gráficos
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Gráfico de impedancia
    ax1.semilogx(f, Z_mag, 'b-', linewidth=2, label='Impedancia Infinite Baffle')
    ax1.set_xlabel('Frecuencia (Hz)')
    ax1.set_ylabel('Impedancia (Ω)')
    ax1.set_title('Impedancia - Infinite Baffle (Original)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_ylim(0, 80)
    
    # Gráfico de SPL
    ax2.semilogx(f, spl, 'r-', linewidth=2, label='SPL Infinite Baffle')
    ax2.set_xlabel('Frecuencia (Hz)')
    ax2.set_ylabel('SPL (dB)')
    ax2.set_title('SPL - Infinite Baffle (Original)')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_ylim(-20, 120)
    
    plt.tight_layout()
    plt.savefig('outputs/test_infinite_baffle_original.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    # Verificar características del infinite baffle
    print("✅ Infinite Baffle - Verificación Original:")
    print(f"   Impedancia: {Z_mag.min():.1f} - {Z_mag.max():.1f} Ω")
    print(f"   SPL: {spl.min():.1f} - {spl.max():.1f} dB")
    
    # Buscar pico de impedancia (debería ser uno solo cerca de Fs)
    picos_impedancia = []
    for i in range(1, len(Z_mag)-1):
        if Z_mag[i] > Z_mag[i-1] and Z_mag[i] > Z_mag[i+1] and Z_mag[i] > 20:
            picos_impedancia.append((f[i], Z_mag[i]))
    
    print(f"   Picos de impedancia encontrados: {len(picos_impedancia)}")
    for freq, mag in picos_impedancia:
        print(f"     - {freq:.1f} Hz: {mag:.1f} Ω")
        
    if len(picos_impedancia) == 1:
        print("✅ CORRECTO: Un solo pico de impedancia como debe ser en infinite baffle")
    else:
        print("❌ ERROR: Múltiples picos de impedancia")
        
except Exception as e:
    print(f"❌ Error en simulación infinite baffle: {e}")
    import traceback
    traceback.print_exc()

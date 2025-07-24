# test_comparacion_final.py
# Test para verificar que tanto infinite baffle como bass-reflex funcionan correctamente

import numpy as np
import matplotlib.pyplot as plt
from core.driver import Driver
from core.bassreflex import BassReflexBox

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
    "Mms": 0.02,
    "Cms": 0.001
}

# Frecuencias de prueba
f = np.logspace(1, 4, 1000)  # 10 Hz a 10 kHz

print("=== VERIFICACIÓN FINAL ===")

# Test 1: Infinite Baffle
try:
    driver_ib = Driver(driver_params, enclosure=None)
    Z_ib = np.abs(driver_ib.impedance(f))
    spl_ib = driver_ib.spl_total(f, U=2.83)
    
    # Contar picos de impedancia
    picos_ib = 0
    for i in range(1, len(Z_ib)-1):
        if Z_ib[i] > Z_ib[i-1] and Z_ib[i] > Z_ib[i+1] and Z_ib[i] > 20:
            picos_ib += 1
    
    print(f"✅ Infinite Baffle:")
    print(f"   Impedancia: {Z_ib.min():.1f} - {Z_ib.max():.1f} Ω")
    print(f"   SPL: {spl_ib.min():.1f} - {spl_ib.max():.1f} dB")
    print(f"   Picos de impedancia: {picos_ib} (debe ser 1)")
    
except Exception as e:
    print(f"❌ Error Infinite Baffle: {e}")

# Test 2: Bass-Reflex  
try:
    enclosure_br = BassReflexBox(
        vb_litros=30,       # Volumen en litros
        area_port=0.005,    # Área del puerto en m²
        length_port=0.05    # Longitud del puerto en m
    )
    driver_br = Driver(driver_params, enclosure=enclosure_br)
    Z_br = np.abs(driver_br.impedance(f))
    spl_br_total = driver_br.spl_bassreflex_total(f, U=2.83)
    
    # Contar picos de impedancia
    picos_br = 0
    for i in range(1, len(Z_br)-1):
        if Z_br[i] > Z_br[i-1] and Z_br[i] > Z_br[i+1] and Z_br[i] > 25:
            picos_br += 1
    
    print(f"✅ Bass-Reflex:")
    print(f"   Impedancia: {Z_br.min():.1f} - {Z_br.max():.1f} Ω")
    print(f"   SPL Total: {spl_br_total.min():.1f} - {spl_br_total.max():.1f} dB")
    print(f"   Picos de impedancia: {picos_br} (debe ser 2)")
    
    bassreflex_ok = True
    
except Exception as e:
    print(f"❌ Error Bass-Reflex: {e}")
    bassreflex_ok = False
    Z_br = np.zeros_like(f)  # Array de ceros para evitar error en gráficos
    spl_br_total = np.zeros_like(f)
    picos_br = 0

# Test 3: Crear gráfico comparativo
try:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Gráfico de impedancia
    ax1.semilogx(f, Z_ib, 'b-', linewidth=2, label='Infinite Baffle (1 pico)')
    ax1.semilogx(f, Z_br, 'r-', linewidth=2, label='Bass-Reflex (2 picos)')
    ax1.set_xlabel('Frecuencia (Hz)')
    ax1.set_ylabel('Impedancia (Ω)')
    ax1.set_title('Comparación Impedancia - Restaurado')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_ylim(0, 100)
    
    # Gráfico de SPL
    ax2.semilogx(f, spl_ib, 'b-', linewidth=2, label='Infinite Baffle')
    ax2.semilogx(f, spl_br_total, 'r-', linewidth=2, label='Bass-Reflex')
    ax2.set_xlabel('Frecuencia (Hz)')
    ax2.set_ylabel('SPL (dB)')
    ax2.set_title('Comparación SPL - Restaurado')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_ylim(0, 130)
    
    plt.tight_layout()
    plt.savefig('outputs/comparacion_restaurado.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print("\n✅ ESTADO FINAL:")
    if picos_ib == 1 and (bassreflex_ok and picos_br == 2):
        print("✅ PERFECTO: Infinite baffle con 1 pico, Bass-reflex con 2 picos")
        print("✅ Sistema restaurado correctamente como estaba originalmente")
    elif picos_ib == 1:
        print("✅ PARCIAL: Infinite baffle restaurado (1 pico), Bass-reflex pendiente")
    else:
        print("❌ Algo sigue mal con los picos")
        
except Exception as e:
    print(f"❌ Error en gráficos: {e}")
    import traceback
    traceback.print_exc()

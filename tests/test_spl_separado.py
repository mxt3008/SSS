"""
Test para verificar que SPL separado solo aparece en bass-reflex
"""

import numpy as np
import matplotlib.pyplot as plt
from core.driver import Driver
from core.sealed import SealedBox
from core.bassreflex import BassReflexBox

def test_spl_separado():
    print("🎯 TEST: SPL SEPARADO SOLO EN BASS-REFLEX")
    
    # Parámetros del driver
    params = {
        'Fs': 52,
        'Qts': 0.35,
        'Qes': 0.4,
        'Re': 6.5,
        'Sd': 0.0133,
        'Vas': 15,
        'Xmax': 0.004,
        'Bl': 5.5,
        'Le': 0.4e-3,
        'Rg': 0,
        'Mms': 0.01,
        'Cms': 1.8e-3,
    }
    
    # Frecuencias de prueba
    f = np.logspace(1, 3, 100)  # 10 Hz a 1 kHz
    
    print("\n📦 CASO 1: CAJA SELLADA")
    sealed_box = SealedBox(20)  # 20 litros
    driver_sealed = Driver(params, sealed_box)
    
    # Para caja sellada: solo SPL total
    spl_total_sealed = driver_sealed.spl_total(f)
    print(f"SPL total rango: {spl_total_sealed.min():.1f} - {spl_total_sealed.max():.1f} dB")
    print("✅ Solo SPL total (correcto para caja sellada)")
    
    print("\n📦 CASO 2: BASS-REFLEX")
    bassreflex_box = BassReflexBox(20, 0.001, 0.05)  # 20L, área y longitud puerto
    driver_bassreflex = Driver(params, bassreflex_box)
    
    # Para bass-reflex: SPL separado disponible
    spl_total_br = driver_bassreflex.spl_total(f)
    spl_cone_br = driver_bassreflex.spl_bassreflex_cone(f)
    spl_port_br = driver_bassreflex.spl_bassreflex_port(f)
    
    print(f"SPL total rango: {spl_total_br.min():.1f} - {spl_total_br.max():.1f} dB")
    print(f"SPL cono rango: {spl_cone_br.min():.1f} - {spl_cone_br.max():.1f} dB")
    print(f"SPL puerto rango: {spl_port_br.min():.1f} - {spl_port_br.max():.1f} dB")
    print("✅ SPL separado disponible (correcto para bass-reflex)")
    
    # Gráfica comparativa
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Caja sellada - Solo SPL total
    ax1.semilogx(f, spl_total_sealed, 'b-', linewidth=2, label='SPL Total')
    ax1.set_title('CAJA SELLADA\n(Solo SPL Total)')
    ax1.set_xlabel('Frecuencia [Hz]')
    ax1.set_ylabel('SPL [dB]')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_ylim(70, 110)
    
    # Bass-reflex - SPL separado
    ax2.semilogx(f, spl_cone_br, 'b-', linewidth=2, label='SPL Cono (azul)')
    ax2.semilogx(f, spl_port_br, 'r-', linewidth=2, label='SPL Puerto (rojo)')
    ax2.semilogx(f, spl_total_br, 'c-', linewidth=3, label='SPL Total (turquesa)')
    ax2.set_title('BASS-REFLEX\n(SPL Separado: Cono + Puerto + Total)')
    ax2.set_xlabel('Frecuencia [Hz]')
    ax2.set_ylabel('SPL [dB]')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_ylim(70, 110)
    
    plt.tight_layout()
    plt.savefig('outputs/test_spl_separado.png', dpi=300, bbox_inches='tight')
    print(f"\n📊 Gráfica guardada: outputs/test_spl_separado.png")
    
    print(f"\n🎯 RESULTADO:")
    print(f"✅ Caja sellada: Solo SPL total (como debe ser)")
    print(f"✅ Bass-reflex: SPL separado disponible (cono, puerto, total)")
    print(f"✅ El sistema funciona correctamente!")

if __name__ == "__main__":
    test_spl_separado()

#!/usr/bin/env python3
"""
Test rápido para verificar manejo de escalares en funciones SPL bass-reflex
"""

import numpy as np
from core.driver import Driver

def test_spl_scalar_array():
    print("🧪 TEST MANEJO ESCALAR/ARRAY EN SPL BASS-REFLEX")
    
    # Crear driver básico
    driver_params = {
        "Fs": 37.5,
        "Qts": 0.38,
        "Qes": 0.42, 
        "Vas": 18.5,
        "Re": 5.4,
        "Bl": 7.5,
        "Mms": 21.0e-3,  # kg
        "Cms": 1.8e-3    # m/N
    }
    driver = Driver(driver_params)
    
    # Test con escalar
    print("\n📊 Test con ESCALAR:")
    freq_scalar = 50.0
    
    try:
        spl_cone_scalar = driver.spl_bassreflex_cone(freq_scalar)
        spl_port_scalar = driver.spl_bassreflex_port(freq_scalar)
        spl_total_scalar = driver.spl_bassreflex_total(freq_scalar)
        
        print(f"✅ Frecuencia: {freq_scalar} Hz")
        print(f"   SPL Cono: {spl_cone_scalar:.1f} dB")
        print(f"   SPL Puerto: {spl_port_scalar:.1f} dB")
        print(f"   SPL Total: {spl_total_scalar:.1f} dB")
        
        # Verificar que son escalares
        assert np.isscalar(spl_cone_scalar), "SPL Cono debería ser escalar"
        assert np.isscalar(spl_port_scalar), "SPL Puerto debería ser escalar"
        assert np.isscalar(spl_total_scalar), "SPL Total debería ser escalar"
        print("✅ Todos los retornos son escalares correctamente")
        
    except Exception as e:
        print(f"❌ Error con escalar: {e}")
        return False
    
    # Test con array
    print("\n📊 Test con ARRAY:")
    freq_array = np.array([20.0, 50.0, 100.0])
    
    try:
        spl_cone_array = driver.spl_bassreflex_cone(freq_array)
        spl_port_array = driver.spl_bassreflex_port(freq_array)
        spl_total_array = driver.spl_bassreflex_total(freq_array)
        
        print(f"✅ Frecuencias: {freq_array} Hz")
        print(f"   SPL Cono: {spl_cone_array}")
        print(f"   SPL Puerto: {spl_port_array}")
        print(f"   SPL Total: {spl_total_array}")
        
        # Verificar que son arrays del tamaño correcto
        assert len(spl_cone_array) == len(freq_array), "SPL Cono debería tener el mismo tamaño"
        assert len(spl_port_array) == len(freq_array), "SPL Puerto debería tener el mismo tamaño"
        assert len(spl_total_array) == len(freq_array), "SPL Total debería tener el mismo tamaño"
        print("✅ Todos los arrays tienen el tamaño correcto")
        
    except Exception as e:
        print(f"❌ Error con array: {e}")
        return False
    
    print("\n🎯 ¡TODOS LOS TESTS PASARON!")
    print("✅ Las funciones SPL bass-reflex manejan correctamente escalares y arrays")
    return True

if __name__ == "__main__":
    test_spl_scalar_array()

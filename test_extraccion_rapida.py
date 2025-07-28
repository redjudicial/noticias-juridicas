#!/usr/bin/env python3
"""
Script para probar extracción rápida con pocas noticias
"""

import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.main import NoticiasJuridicasSystem

def test_extraccion_rapida():
    """Probar extracción rápida con pocas noticias"""
    print("🧪 **TEST DE EXTRACCIÓN RÁPIDA**")
    print("=" * 40)
    
    # Inicializar sistema
    sistema = NoticiasJuridicasSystem()
    
    # Configurar para extracción rápida
    sistema.config['max_noticias_por_fuente'] = 2  # Solo 2 noticias por fuente
    
    print(f"\n📊 **CONFIGURACIÓN DE PRUEBA**")
    print(f"   • Máximo noticias por fuente: {sistema.config['max_noticias_por_fuente']}")
    print(f"   • Modo: PRODUCCIÓN")
    
    # Ejecutar extracción
    print(f"\n🔄 **INICIANDO EXTRACCIÓN DE PRUEBA**")
    print("-" * 40)
    
    try:
        sistema.run_scraping_completo()
        
        print(f"\n✅ **PRUEBA COMPLETADA**")
        print("=" * 40)
        print("✅ Proceso finalizado exitosamente")
        print(f"⏰ Tiempo: {datetime.now().strftime('%H:%M:%S')}")
            
    except Exception as e:
        print(f"\n❌ **ERROR EN LA PRUEBA**")
        print(f"   Error: {e}")
        return

if __name__ == "__main__":
    test_extraccion_rapida() 
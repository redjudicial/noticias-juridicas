#!/usr/bin/env python3
"""
Script para extracción completa de noticias desde el Lunes 21 de Julio
PASO 3 del pipeline: Extracción completa con todas las fuentes
"""

import sys
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.main import NoticiasJuridicasSystem

def extraccion_completa():
    """Ejecutar extracción completa de noticias"""
    print("🚀 **PASO 3: EXTRACCIÓN COMPLETA DE NOTICIAS**")
    print("=" * 60)
    print("📅 Desde: Lunes 21 de Julio de 2025")
    print("📅 Hasta: Hoy")
    print("=" * 60)
    
    # Inicializar sistema
    sistema = NoticiasJuridicasSystem()
    
    # Configurar para extracción completa
    config = {
        'max_noticias_por_fuente': 50,  # Más noticias por fuente
        'incluir_fuentes_problematicas': True,  # Incluir todas las fuentes
        'modo_test': False,  # Modo producción
        'fecha_desde': '2025-07-21',  # Desde Lunes 21 de Julio
        'fecha_hasta': datetime.now().strftime('%Y-%m-%d')  # Hasta hoy
    }
    
    print("\n📊 **CONFIGURACIÓN DE EXTRACCIÓN**")
    print(f"   • Máximo noticias por fuente: {config['max_noticias_por_fuente']}")
    print(f"   • Fecha desde: {config['fecha_desde']}")
    print(f"   • Fecha hasta: {config['fecha_hasta']}")
    print(f"   • Modo: {'PRODUCCIÓN' if not config['modo_test'] else 'TEST'}")
    
    # Confirmar inicio
    print(f"\n⚠️  ¿Estás listo para iniciar la extracción completa?")
    print("Esto puede tomar varios minutos...")
    
    confirmacion = input("Escribe 'SI' para continuar: ")
    
    if confirmacion != 'SI':
        print("❌ Extracción cancelada")
        return
    
    # Ejecutar extracción
    print("\n🔄 **INICIANDO EXTRACCIÓN COMPLETA**")
    print("-" * 40)
    
    try:
        # Ejecutar scraping completo
        sistema.run_scraping_completo()
        
        # Mostrar resultados
        print("\n📈 **EXTRACCIÓN COMPLETADA**")
        print("=" * 40)
        print("✅ Proceso finalizado exitosamente")
        print(f"⏰ Tiempo: {datetime.now().strftime('%H:%M:%S')}")
            
    except Exception as e:
        print(f"\n❌ **ERROR EN LA EXTRACCIÓN**")
        print(f"   Error: {e}")
        return
    
    print("\n" + "=" * 60)
    print("🏁 **PASO 3 COMPLETADO**")
    print("📋 Próximo paso: Configurar GitHub Actions para ejecución automática")

if __name__ == "__main__":
    extraccion_completa() 
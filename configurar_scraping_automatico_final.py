#!/usr/bin/env python3
"""
Script para configurar scraping automático con tribunales ambientales unificados
"""

import os
import sys
import time
from datetime import datetime, timezone
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.main import NoticiasJuridicasSystem

def main():
    """Ejecutar scraping con configuraciones actualizadas"""
    print("🚀 INICIANDO SCRAPING CON TRIBUNALES AMBIENTALES UNIFICADOS")
    print("=" * 60)
    print(f"⏰ Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Inicializar sistema
        sistema = NoticiasJuridicasSystem()
        
        # Ejecutar scraping completo
        print("🔄 Ejecutando scraping completo...")
        resultado = sistema.run_scraping_completo()
        
        print()
        print("✅ SCRAPING COMPLETADO")
        print("=" * 40)
        print(f"📊 Noticias nuevas: {resultado.get('nuevas', 0)}")
        print(f"🔄 Noticias actualizadas: {resultado.get('actualizadas', 0)}")
        print(f"❌ Errores: {len(resultado.get('errores', []))}")
        print(f"⏰ Hora de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Mostrar errores si los hay
        if resultado.get('errores'):
            print()
            print("⚠️ ERRORES ENCONTRADOS:")
            for error in resultado['errores']:
                print(f"   - {error}")
        
        # Mostrar estadísticas
        print()
        print("📈 ESTADÍSTICAS DEL SISTEMA:")
        stats = sistema.get_estadisticas()
        for fuente, datos in stats.items():
            print(f"   {fuente}: {datos['total']} noticias")
        
        print()
        print("🎯 CAMBIOS APLICADOS:")
        print("   ✅ Tribunales ambientales unificados bajo 'Tribunal Ambiental'")
        print("   ✅ Prefijos agregados: (1º), (2º), (3º)")
        print("   ✅ Sistema anti-duplicados activado")
        print("   ✅ Resúmenes de 8 líneas configurados")
        
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 
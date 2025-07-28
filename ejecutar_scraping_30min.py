#!/usr/bin/env python3
"""
Script para ejecutar scraping cada 30 minutos con tribunales ambientales unificados
"""

import os
import sys
import time
import schedule
from datetime import datetime, timezone
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.main import NoticiasJuridicasSystem

def ejecutar_scraping():
    """Ejecutar una ronda de scraping"""
    print(f"\n🔄 EJECUTANDO SCRAPING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Inicializar sistema
        sistema = NoticiasJuridicasSystem()
        
        # Ejecutar scraping completo
        resultado = sistema.run_scraping_completo()
        
        print(f"✅ SCRAPING COMPLETADO - {datetime.now().strftime('%H:%M:%S')}")
        print(f"📊 Nuevas: {resultado.get('nuevas', 0)} | Actualizadas: {resultado.get('actualizadas', 0)} | Errores: {len(resultado.get('errores', []))}")
        
        # Mostrar errores si los hay
        if resultado.get('errores'):
            print("⚠️ Errores encontrados:")
            for error in resultado['errores'][:3]:  # Solo mostrar los primeros 3
                print(f"   - {error}")
            if len(resultado['errores']) > 3:
                print(f"   ... y {len(resultado['errores']) - 3} más")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {str(e)}")
        return False

def main():
    """Función principal con programación cada 30 minutos"""
    print("🚀 SISTEMA DE SCRAPING AUTOMÁTICO - TRIBUNALES AMBIENTALES UNIFICADOS")
    print("=" * 70)
    print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔄 Intervalo: Cada 30 minutos")
    print("🎯 Cambios aplicados:")
    print("   ✅ Tribunales ambientales unificados bajo 'Tribunal Ambiental'")
    print("   ✅ Prefijos agregados: (1º), (2º), (3º)")
    print("   ✅ Sistema anti-duplicados activado")
    print("   ✅ Resúmenes de 8 líneas configurados")
    print("=" * 70)
    
    # Programar ejecución cada 30 minutos
    schedule.every(30).minutes.do(ejecutar_scraping)
    
    # Ejecutar inmediatamente la primera vez
    print("\n🚀 Ejecutando primera ronda inmediatamente...")
    ejecutar_scraping()
    
    print(f"\n⏰ Próxima ejecución programada: {datetime.now().strftime('%H:%M')}")
    print("🔄 Sistema en ejecución. Presiona Ctrl+C para detener.")
    
    # Bucle principal
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar cada minuto
            
    except KeyboardInterrupt:
        print("\n\n🛑 SISTEMA DETENIDO POR EL USUARIO")
        print(f"⏰ Detenido: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 
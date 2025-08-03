#!/usr/bin/env python3
"""
Ejecutar scraping manual inmediatamente
"""

import subprocess
import sys
import os
from datetime import datetime

def ejecutar_scraping():
    """Ejecutar scraping manual"""
    print("🚀 **EJECUTANDO SCRAPING MANUAL INMEDIATO**")
    print("=" * 50)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Ejecutar scraping con parámetros optimizados
        comando = [
            'python3', 'backend/main.py',
            '--once',
            '--working-only',
            '--max-noticias', '5'
        ]
        
        print(f"🔧 Comando: {' '.join(comando)}")
        print("⏳ Ejecutando...")
        
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutos máximo
            cwd=os.getcwd()
        )
        
        print("✅ Scraping completado")
        print(f"📊 Código de salida: {resultado.returncode}")
        
        if resultado.stdout:
            print("📤 Salida:")
            print(resultado.stdout)
        
        if resultado.stderr:
            print("⚠️ Errores:")
            print(resultado.stderr)
            
        return resultado.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Timeout: El scraping tardó más de 5 minutos")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando scraping: {e}")
        return False

def verificar_resultados():
    """Verificar si se agregaron nuevas noticias"""
    print("\n🔍 **VERIFICANDO RESULTADOS**")
    print("=" * 50)
    
    try:
        # Importar el script de verificación
        from verificar_datos_supabase import obtener_noticias_recientes
        
        noticias = obtener_noticias_recientes()
        if noticias:
            print(f"📊 Total noticias recientes: {len(noticias)}")
            print(f"📰 Última noticia: {noticias[0]['titulo'][:50]}...")
            print(f"🕐 Fecha: {noticias[0]['fecha_publicacion']}")
        else:
            print("❌ No se pudieron obtener noticias")
            
    except Exception as e:
        print(f"❌ Error verificando resultados: {e}")

def main():
    """Función principal"""
    print("🎯 **SCRAPING MANUAL INMEDIATO**")
    print("=" * 60)
    
    # Ejecutar scraping
    exito = ejecutar_scraping()
    
    if exito:
        print("\n✅ Scraping ejecutado exitosamente")
        verificar_resultados()
    else:
        print("\n❌ El scraping falló")
    
    print("\n" + "=" * 60)
    print("✅ **PROCESO COMPLETADO**")

if __name__ == "__main__":
    main() 
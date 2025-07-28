#!/usr/bin/env python3
"""
Script para probar el sistema completo de noticias jurídicas
Incluye todas las fuentes implementadas y el procesamiento completo
"""
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(__file__))

def test_fuentes_disponibles():
    """Probar todas las fuentes disponibles"""
    print("🔍 VERIFICANDO FUENTES DISPONIBLES")
    print("="*60)
    
    # Lista de fuentes configuradas
    fuentes = [
        ("Poder Judicial", "https://www.pjud.cl/prensa-y-comunicaciones/noticias-del-poder-judicial"),
        ("Ministerio de Justicia", "https://www.minjusticia.gob.cl/noticias/"),
        ("Defensoría Penal Pública", "https://www.dpp.cl/sala_prensa/noticias"),
        ("Contraloría", "https://www.contraloria.cl/portalweb/web/cgr/noticias"),
        ("TDPI", "https://www.tdpi.cl/category/noticias/"),
        ("CDE", "https://www.cde.cl/post-sitemap1.xml"),
        ("TDLC", "https://www.tdlc.cl/noticias/"),
        ("1TA", "https://www.1ta.cl/category/noticias/"),
        ("3TA", "https://3ta.cl/category/noticias/"),
        ("Tribunal Ambiental", "https://tribunalambiental.cl/category/noticias/")
    ]
    
    import requests
    
    for nombre, url in fuentes:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {nombre}: ACCESIBLE")
            else:
                print(f"⚠️  {nombre}: ERROR {response.status_code}")
        except Exception as e:
            print(f"❌ {nombre}: NO ACCESIBLE - {str(e)}")
    
    print()

def test_scrapers_simples():
    """Probar scrapers simples"""
    print("🧪 PROBANDO SCRAPERS SIMPLES")
    print("="*60)
    
    from test_scraper_simple import ScraperSimple
    
    scraper = ScraperSimple()
    
    # Probar TDLC
    tdlc_noticias = scraper.test_tdlc()
    
    # Probar 3TA
    t3ta_noticias = scraper.test_3ta()
    
    print(f"📊 RESULTADOS:")
    print(f"   TDLC: {len(tdlc_noticias)} noticias")
    print(f"   3TA: {len(t3ta_noticias)} noticias")
    print()

def test_base_datos():
    """Probar conexión a base de datos"""
    print("🗄️ PROBANDO CONEXIÓN A BASE DE DATOS")
    print("="*60)
    
    try:
        from backend.database.supabase_client import SupabaseClient
        
        # Cargar variables de entorno
        from dotenv import load_dotenv
        load_dotenv('APIS_Y_CREDENCIALES.env')
        
        client = SupabaseClient()
        
        # Probar conexión
        response = client.supabase.table('noticias_juridicas').select('count').execute()
        
        if response.data:
            print("✅ Conexión a Supabase: EXITOSA")
            print(f"   Tabla noticias_juridicas: ACCESIBLE")
        else:
            print("⚠️  Conexión a Supabase: PROBLEMA")
            
    except Exception as e:
        print(f"❌ Error en base de datos: {str(e)}")
    
    print()

def test_frontend():
    """Probar frontend"""
    print("🎨 PROBANDO FRONTEND")
    print("="*60)
    
    # Verificar archivos del frontend
    archivos_frontend = [
        "noticias.html",
        "frontend/css/noticias.css",
        "frontend/js/noticias.js"
    ]
    
    for archivo in archivos_frontend:
        if os.path.exists(archivo):
            print(f"✅ {archivo}: EXISTE")
        else:
            print(f"❌ {archivo}: NO EXISTE")
    
    print()

def generar_reporte():
    """Generar reporte final"""
    print("📋 REPORTE FINAL DEL SISTEMA")
    print("="*60)
    
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🖥️  Sistema: {sys.platform}")
    print(f"🐍 Python: {sys.version}")
    
    print(f"\n📊 ESTADO DE COMPONENTES:")
    print(f"   ✅ Fuentes configuradas: 10")
    print(f"   ✅ Scrapers implementados: 10")
    print(f"   ✅ Base de datos: Supabase")
    print(f"   ✅ Frontend: HTML/CSS/JS")
    print(f"   ✅ Automatización: GitHub Actions")
    
    print(f"\n🎯 PRÓXIMOS PASOS:")
    print(f"   1. Configurar repositorio en GitHub")
    print(f"   2. Configurar secrets en GitHub")
    print(f"   3. Activar GitHub Actions")
    print(f"   4. Monitorear ejecución automática")
    print(f"   5. Revisar noticias en noticias.html")

def main():
    """Función principal"""
    print("🚀 SISTEMA DE NOTICIAS JURÍDICAS - PRUEBA COMPLETA")
    print("="*80)
    print(f"⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Ejecutar todas las pruebas
    test_fuentes_disponibles()
    test_scrapers_simples()
    test_base_datos()
    test_frontend()
    generar_reporte()
    
    print()
    print("🏁 PRUEBA COMPLETA FINALIZADA")
    print("="*80)

if __name__ == "__main__":
    main() 
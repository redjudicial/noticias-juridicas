#!/usr/bin/env python3
"""
Verificación final completa del sistema de noticias
Comprueba que todo esté funcionando correctamente
"""

import os
import sys
import requests
import subprocess
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

# Configuración de Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://qfomiierchksyfhxoukj.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def verificar_base_datos():
    """Verificar estado de la base de datos"""
    print("🗄️ **VERIFICACIÓN DE BASE DE DATOS**")
    print("-" * 50)
    
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}'
        }
        
        # Obtener todas las noticias
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&order=fecha_publicacion.desc',
            headers=headers
        )
        
        if response.status_code == 200:
            noticias = response.json()
            print(f"✅ Conexión exitosa")
            print(f"📊 Total noticias: {len(noticias)}")
            
            # Verificar noticias recientes
            fecha_limite = datetime.now().replace(tzinfo=None) - timedelta(hours=24)
            recientes = 0
            
            for noticia in noticias:
                fecha = datetime.fromisoformat(noticia['fecha_publicacion'].replace('Z', '+00:00')).replace(tzinfo=None)
                if fecha > fecha_limite:
                    recientes += 1
            
            print(f"📈 Noticias últimas 24h: {recientes}")
            
            if recientes > 0:
                print("✅ Base de datos activa con noticias recientes")
                return True
            else:
                print("⚠️ No hay noticias recientes")
                return False
        else:
            print(f"❌ Error de conexión: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        return False

def verificar_scrapers():
    """Verificar que todos los scrapers funcionan"""
    print("\n🔧 **VERIFICACIÓN DE SCRAPERS**")
    print("-" * 50)
    
    scrapers = [
        'poder_judicial', 'contraloria', 'cde', 'tdlc', '1ta', '3ta',
        'tribunal_ambiental', 'sii', 'tta', 'inapi', 'dt', 'tdpi', 'ministerio_justicia'
    ]
    
    resultados = {}
    
    for scraper in scrapers:
        archivo_test = f"test_{scraper}_scraper.py"
        
        if os.path.exists(archivo_test):
            try:
                resultado = subprocess.run(
                    ['python3', archivo_test],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                resultados[scraper] = resultado.returncode == 0
                
                if resultados[scraper]:
                    print(f"✅ {scraper}: Funciona")
                else:
                    print(f"❌ {scraper}: Error")
                    
            except subprocess.TimeoutExpired:
                print(f"⏰ {scraper}: Timeout")
                resultados[scraper] = False
            except Exception as e:
                print(f"❌ {scraper}: Error - {e}")
                resultados[scraper] = False
        else:
            print(f"⚠️ {scraper}: Sin test disponible")
            resultados[scraper] = False
    
    return resultados

def verificar_github_actions():
    """Verificar configuración de GitHub Actions"""
    print("\n🤖 **VERIFICACIÓN DE GITHUB ACTIONS**")
    print("-" * 50)
    
    workflow_file = ".github/workflows/scraping_automatico_optimizado.yml"
    
    if not os.path.exists(workflow_file):
        print("❌ Archivo de workflow no encontrado")
        return False
    
    try:
        with open(workflow_file, 'r') as f:
            content = f.read()
        
        # Verificar configuración 24/7
        if "cron: '0 * * * *'" in content:
            print("✅ Configuración 24/7 cada hora correcta")
            return True
        else:
            print("❌ Configuración de cron incorrecta")
            return False
            
    except Exception as e:
        print(f"❌ Error leyendo workflow: {e}")
        return False

def verificar_frontend():
    """Verificar estado del frontend"""
    print("\n🌐 **VERIFICACIÓN DEL FRONTEND**")
    print("-" * 50)
    
    archivos_requeridos = [
        'frontend/index.html',
        'frontend/js/noticias.js',
        'frontend/css/noticias.css'
    ]
    
    archivos_ok = 0
    
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"✅ {archivo}: Encontrado")
            archivos_ok += 1
        else:
            print(f"❌ {archivo}: No encontrado")
    
    # Verificar actualización automática
    if os.path.exists('frontend/js/noticias.js'):
        with open('frontend/js/noticias.js', 'r') as f:
            content = f.read()
        
        if 'setInterval' in content and 'cargarNoticias' in content:
            print("✅ Actualización automática configurada")
            archivos_ok += 1
        else:
            print("❌ Actualización automática no configurada")
    
    return archivos_ok >= len(archivos_requeridos)

def verificar_scraping_completo():
    """Verificar que el scraping completo funciona"""
    print("\n🚀 **VERIFICACIÓN DE SCRAPING COMPLETO**")
    print("-" * 50)
    
    try:
        resultado = subprocess.run([
            'python3', 'backend/main.py', '--once', '--max-noticias', '2'
        ], capture_output=True, text=True, timeout=180)
        
        if resultado.returncode == 0:
            print("✅ Scraping completo funciona correctamente")
            return True
        else:
            print("❌ Error en scraping completo")
            print(f"Error: {resultado.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout en scraping completo")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando scraping: {e}")
        return False

def generar_reporte_final():
    """Generar reporte final del sistema"""
    print("\n📊 **REPORTE FINAL DEL SISTEMA**")
    print("=" * 60)
    
    # Ejecutar verificaciones
    db_ok = verificar_base_datos()
    scrapers_resultados = verificar_scrapers()
    github_ok = verificar_github_actions()
    frontend_ok = verificar_frontend()
    scraping_ok = verificar_scraping_completo()
    
    # Calcular métricas
    scrapers_funcionando = sum(1 for r in scrapers_resultados.values() if r)
    total_scrapers = len(scrapers_resultados)
    
    print(f"\n📈 **MÉTRICAS FINALES:**")
    print("-" * 40)
    print(f"Base de datos: {'✅ OK' if db_ok else '❌ ERROR'}")
    print(f"Scrapers: {scrapers_funcionando}/{total_scrapers} funcionando")
    print(f"GitHub Actions: {'✅ OK' if github_ok else '❌ ERROR'}")
    print(f"Frontend: {'✅ OK' if frontend_ok else '❌ ERROR'}")
    print(f"Scraping completo: {'✅ OK' if scraping_ok else '❌ ERROR'}")
    
    # Calcular score general
    score = 0
    total_checks = 5
    
    if db_ok: score += 1
    if scrapers_funcionando >= total_scrapers * 0.8: score += 1  # 80% de scrapers funcionando
    if github_ok: score += 1
    if frontend_ok: score += 1
    if scraping_ok: score += 1
    
    porcentaje = (score / total_checks) * 100
    
    print(f"\n🎯 **SCORE GENERAL: {porcentaje:.1f}%**")
    
    if porcentaje >= 90:
        print("🏆 ¡EXCELENTE! El sistema está funcionando perfectamente")
    elif porcentaje >= 70:
        print("✅ BUENO - El sistema funciona bien con algunas mejoras menores")
    elif porcentaje >= 50:
        print("⚠️ REGULAR - El sistema necesita mejoras importantes")
    else:
        print("❌ CRÍTICO - El sistema necesita reparación urgente")
    
    # Recomendaciones
    print(f"\n💡 **RECOMENDACIONES:**")
    print("-" * 40)
    
    if not db_ok:
        print("🔧 Reparar conexión a base de datos")
    
    if scrapers_funcionando < total_scrapers * 0.8:
        print("🔧 Reparar scrapers que no funcionan")
    
    if not github_ok:
        print("🔧 Corregir configuración de GitHub Actions")
    
    if not frontend_ok:
        print("🔧 Reparar archivos del frontend")
    
    if not scraping_ok:
        print("🔧 Corregir scraping completo")
    
    if porcentaje >= 90:
        print("🎉 ¡El sistema está listo para producción!")

def main():
    """Función principal"""
    print("🔍 **VERIFICACIÓN FINAL COMPLETA DEL SISTEMA**")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    generar_reporte_final()
    
    print(f"\n✅ **VERIFICACIÓN COMPLETADA**")
    print("=" * 70)

if __name__ == "__main__":
    main() 
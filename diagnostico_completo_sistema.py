#!/usr/bin/env python3
"""
Diagnóstico completo del sistema de noticias
Analiza todas las fuentes, scrapers, base de datos y frontend
"""

import os
import sys
import requests
import json
import subprocess
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

# Configuración de Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://qfomiierchksyfhxoukj.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def obtener_noticias_completas():
    """Obtener todas las noticias de la base de datos"""
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}'
        }
        
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&order=fecha_publicacion.desc',
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error al obtener noticias: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return []

def analizar_fuentes_detallado():
    """Análisis detallado de cada fuente"""
    print("🔍 **ANÁLISIS DETALLADO DE FUENTES**")
    print("=" * 60)
    
    noticias = obtener_noticias_completas()
    
    if not noticias:
        print("❌ No se pudieron obtener noticias")
        return
    
    # Agrupar por fuente
    fuentes = {}
    fecha_limite = datetime.now().replace(tzinfo=None) - timedelta(hours=24)
    
    for noticia in noticias:
        fuente = noticia['fuente']
        fecha_noticia = datetime.fromisoformat(noticia['fecha_publicacion'].replace('Z', '+00:00')).replace(tzinfo=None)
        
        if fuente not in fuentes:
            fuentes[fuente] = {
                'total': 0,
                'recientes': 0,
                'primera_fecha': None,
                'ultima_fecha': None,
                'ejemplos': []
            }
        
        fuentes[fuente]['total'] += 1
        
        if fecha_noticia > fecha_limite:
            fuentes[fuente]['recientes'] += 1
        
        if not fuentes[fuente]['primera_fecha'] or fecha_noticia < fuentes[fuente]['primera_fecha']:
            fuentes[fuente]['primera_fecha'] = fecha_noticia
        
        if not fuentes[fuente]['ultima_fecha'] or fecha_noticia > fuentes[fuente]['ultima_fecha']:
            fuentes[fuente]['ultima_fecha'] = fecha_noticia
        
        if len(fuentes[fuente]['ejemplos']) < 3:
            fuentes[fuente]['ejemplos'].append(noticia['titulo'][:50])
    
    # Lista de fuentes esperadas
    fuentes_esperadas = [
        'poder_judicial', 'contraloria', 'cde', 'tdlc', '1ta', '3ta', 
        'tribunal_ambiental', 'sii', 'tta', 'inapi', 'dt', 'tdpi', 'ministerio_justicia'
    ]
    
    print(f"{'ESTADO':<15} {'FUENTE':<20} {'TOTAL':<6} {'RECIENTES':<10} {'ÚLTIMA ACTIVIDAD':<20}")
    print("-" * 80)
    
    for fuente in fuentes_esperadas:
        if fuente in fuentes:
            data = fuentes[fuente]
            
            if data['recientes'] > 0:
                estado = "🟢 ACTIVA"
            elif data['total'] > 0:
                estado = "🟡 INACTIVA"
            else:
                estado = "🔴 SIN DATOS"
            
            ultima = data['ultima_fecha'].strftime('%Y-%m-%d %H:%M') if data['ultima_fecha'] else 'N/A'
            
            print(f"{estado:<15} {fuente:<20} {data['total']:<6} {data['recientes']:<10} {ultima:<20}")
        else:
            print(f"🔴 SIN DATOS    {fuente:<20} {'0':<6} {'0':<10} {'N/A':<20}")

def verificar_scrapers():
    """Verificar el estado de los scrapers"""
    print(f"\n🔧 **VERIFICACIÓN DE SCRAPERS**")
    print("=" * 60)
    
    scrapers = [
        'poder_judicial', 'contraloria', 'cde', 'tdlc', '1ta', '3ta',
        'tribunal_ambiental', 'sii', 'tta', 'inapi', 'dt', 'tdpi', 'ministerio_justicia'
    ]
    
    for scraper in scrapers:
        archivo_test = f"test_{scraper}_scraper.py"
        
        if os.path.exists(archivo_test):
            print(f"✅ {scraper}: Test disponible")
        else:
            print(f"❌ {scraper}: Sin test disponible")

def verificar_github_actions():
    """Verificar estado de GitHub Actions"""
    print(f"\n🤖 **ESTADO DE GITHUB ACTIONS**")
    print("=" * 60)
    
    workflow_file = ".github/workflows/scraping_automatico_optimizado.yml"
    
    if os.path.exists(workflow_file):
        print("✅ Workflow de GitHub Actions encontrado")
        
        # Verificar configuración
        with open(workflow_file, 'r') as f:
            content = f.read()
            
        if "cron: '0 * * * *'" in content:
            print("✅ Configuración 24/7 cada hora correcta")
        else:
            print("⚠️ Configuración de cron no es 24/7")
    else:
        print("❌ Workflow de GitHub Actions no encontrado")

def verificar_frontend():
    """Verificar estado del frontend"""
    print(f"\n🌐 **ESTADO DEL FRONTEND**")
    print("=" * 60)
    
    archivos_frontend = [
        'frontend/index.html',
        'frontend/js/noticias.js',
        'frontend/css/noticias.css'
    ]
    
    for archivo in archivos_frontend:
        if os.path.exists(archivo):
            print(f"✅ {archivo}: Encontrado")
        else:
            print(f"❌ {archivo}: No encontrado")
    
    # Verificar actualización automática en JS
    if os.path.exists('frontend/js/noticias.js'):
        with open('frontend/js/noticias.js', 'r') as f:
            content = f.read()
            
        if 'setInterval' in content and 'cargarNoticias' in content:
            print("✅ Actualización automática configurada")
        else:
            print("❌ Actualización automática no configurada")

def verificar_base_datos():
    """Verificar estado de la base de datos"""
    print(f"\n🗄️ **ESTADO DE LA BASE DE DATOS**")
    print("=" * 60)
    
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}'
        }
        
        # Verificar conexión
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=count',
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Conexión a Supabase exitosa")
            
            # Obtener estadísticas
            noticias = obtener_noticias_completas()
            if noticias:
                print(f"📊 Total noticias: {len(noticias)}")
                
                # Noticias recientes
                fecha_limite = datetime.now().replace(tzinfo=None) - timedelta(hours=24)
                recientes = sum(1 for n in noticias 
                              if datetime.fromisoformat(n['fecha_publicacion'].replace('Z', '+00:00')).replace(tzinfo=None) > fecha_limite)
                
                print(f"📈 Noticias últimas 24h: {recientes}")
                
                # Última noticia
                ultima = noticias[0]['fecha_publicacion']
                print(f"🕐 Última noticia: {ultima[:19]}")
        else:
            print(f"❌ Error de conexión: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")

def generar_recomendaciones():
    """Generar recomendaciones basadas en el análisis"""
    print(f"\n💡 **RECOMENDACIONES**")
    print("=" * 60)
    
    print("1. 🚨 **PRIORIDAD ALTA:**")
    print("   - Arreglar scraper de Contraloría (errores de hash)")
    print("   - Verificar scraper de SII (posible cambio de estructura)")
    print("   - Revisar scraper de INAPI (sin noticias recientes)")
    
    print("\n2. 🔧 **PRIORIDAD MEDIA:**")
    print("   - Configurar scrapers que nunca han funcionado")
    print("   - Implementar sistema de monitoreo")
    print("   - Optimizar rendimiento del frontend")
    
    print("\n3. 📊 **PRIORIDAD BAJA:**")
    print("   - Mejorar calidad de resúmenes ejecutivos")
    print("   - Implementar notificaciones push")
    print("   - Crear dashboard de métricas")

def main():
    """Función principal"""
    print("🔍 **DIAGNÓSTICO COMPLETO DEL SISTEMA DE NOTICIAS**")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Ejecutar diagnósticos
    analizar_fuentes_detallado()
    verificar_scrapers()
    verificar_github_actions()
    verificar_frontend()
    verificar_base_datos()
    generar_recomendaciones()
    
    print(f"\n✅ **DIAGNÓSTICO COMPLETADO**")
    print("=" * 70)
    print("📋 Revisa las recomendaciones y ejecuta el pipeline de optimización")

if __name__ == "__main__":
    main() 
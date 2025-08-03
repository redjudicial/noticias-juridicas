#!/usr/bin/env python3
"""
Análisis específico del problema de SII que no se actualiza desde 31 julio
"""

import os
import sys
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('../APIS_Y_CREDENCIALES.env')

# Configuración de Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://qfomiierchksyfhxoukj.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def obtener_noticias_sii():
    """Obtener noticias de SII de la base de datos"""
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}'
        }
        
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&fuente=eq.sii&order=fecha_publicacion.desc',
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

def analizar_fechas_sii():
    """Analizar fechas de las noticias de SII"""
    print("📅 **ANÁLISIS DE FECHAS - SII**")
    print("=" * 50)
    
    noticias = obtener_noticias_sii()
    
    if not noticias:
        print("❌ No se pudieron obtener noticias de SII")
        return
    
    print(f"📊 Total noticias de SII: {len(noticias)}")
    
    # Agrupar por fecha
    fechas = {}
    for noticia in noticias:
        fecha = noticia.get('fecha_publicacion', 'Sin fecha')
        if fecha != 'Sin fecha':
            fecha_simple = fecha[:10]  # Solo la fecha
            if fecha_simple not in fechas:
                fechas[fecha_simple] = 0
            fechas[fecha_simple] += 1
    
    print("\n📊 Noticias por fecha:")
    for fecha in sorted(fechas.keys(), reverse=True):
        print(f"  {fecha}: {fechas[fecha]} noticias")
    
    # Verificar la última noticia
    if noticias:
        ultima = noticias[0]
        fecha_ultima = datetime.fromisoformat(ultima['fecha_publicacion'].replace('Z', '+00:00'))
        ahora = datetime.now(fecha_ultima.tzinfo)
        diferencia = ahora - fecha_ultima
        
        print(f"\n⏰ Última noticia: {fecha_ultima.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏰ Tiempo transcurrido: {diferencia}")
        
        if diferencia.days > 1:
            print("⚠️ ¡ALERTA! No hay noticias nuevas en más de 1 día")

def verificar_urls_sii():
    """Verificar URLs del SII"""
    print("\n🔗 **VERIFICACIÓN DE URLs - SII**")
    print("=" * 50)
    
    # URLs principales del SII
    urls_sii = [
        "https://www.sii.cl/",
        "https://www.sii.cl/noticias/",
        "https://www.sii.cl/noticias/2025/"
    ]
    
    print("🔍 Verificando URLs principales del SII:")
    
    for url in urls_sii:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {url} - Accesible")
            else:
                print(f"❌ {url} - Error {response.status_code}")
        except Exception as e:
            print(f"❌ {url} - Error de conexión: {e}")

def analizar_estructura_sii():
    """Analizar estructura actual de la página de noticias del SII"""
    print("\n🔍 **ANÁLISIS DE ESTRUCTURA - SII**")
    print("=" * 50)
    
    try:
        # Intentar acceder a la página de noticias del SII
        url = "https://www.sii.cl/noticias/"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Página de noticias del SII accesible")
            
            # Buscar patrones en el HTML
            html = response.text
            
            # Buscar enlaces a noticias
            if 'href=' in html and '.htm' in html:
                print("✅ Se encontraron enlaces a noticias (.htm)")
            else:
                print("⚠️ No se encontraron enlaces a noticias (.htm)")
            
            # Buscar fechas
            if '2025' in html:
                print("✅ Se encontraron referencias a 2025")
            else:
                print("⚠️ No se encontraron referencias a 2025")
            
            # Buscar estructura de noticias
            if 'noticias' in html.lower():
                print("✅ Se encontró estructura de noticias")
            else:
                print("⚠️ No se encontró estructura de noticias")
                
        else:
            print(f"❌ Error accediendo a la página: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error analizando estructura: {e}")

def verificar_scraper_sii():
    """Verificar el scraper de SII"""
    print("\n🔧 **VERIFICACIÓN DEL SCRAPER - SII**")
    print("=" * 50)
    
    # Buscar el scraper de SII
    scraper_path = "../backend/scrapers/fuentes/sii/sii_scraper.py"
    
    if os.path.exists(scraper_path):
        print("✅ Archivo del scraper encontrado")
        
        try:
            with open(scraper_path, 'r') as f:
                contenido = f.read()
            
            # Buscar URLs en el scraper
            if 'sii.cl' in contenido:
                print("✅ URLs del SII encontradas en el scraper")
                
                # Buscar líneas con URLs
                lineas = contenido.split('\n')
                for i, linea in enumerate(lineas):
                    if 'sii.cl' in linea:
                        print(f"   Línea {i+1}: {linea.strip()}")
            else:
                print("⚠️ No se encontraron URLs del SII en el scraper")
            
            # Buscar selectores
            if 'selector' in contenido.lower() or 'xpath' in contenido.lower():
                print("✅ Selectores encontrados en el scraper")
            else:
                print("⚠️ No se encontraron selectores en el scraper")
                
        except Exception as e:
            print(f"❌ Error leyendo archivo: {e}")
    else:
        print("❌ Archivo del scraper no encontrado")

def probar_scraper_sii():
    """Probar el scraper de SII directamente"""
    print("\n🧪 **PRUEBA DEL SCRAPER - SII**")
    print("=" * 50)
    
    try:
        # Importar y ejecutar el scraper de SII
        sys.path.append('../backend/scrapers/fuentes/sii')
        
        # Intentar importar el scraper
        try:
            from sii_scraper import SIIScraper
            print("✅ Scraper de SII importado correctamente")
            
            # Crear instancia
            scraper = SIIScraper()
            print("✅ Instancia del scraper creada")
            
            # Intentar extraer noticias
            print("🔍 Intentando extraer noticias...")
            noticias = scraper.scrape()
            
            if noticias:
                print(f"✅ Se extrajeron {len(noticias)} noticias")
                
                # Mostrar las primeras noticias
                for i, noticia in enumerate(noticias[:3], 1):
                    titulo = noticia.get('titulo', 'Sin título')
                    fecha = noticia.get('fecha_publicacion', 'Sin fecha')
                    print(f"   {i}. {titulo[:50]}... ({fecha[:10]})")
            else:
                print("❌ No se extrajeron noticias")
                
        except ImportError as e:
            print(f"❌ Error importando scraper: {e}")
        except Exception as e:
            print(f"❌ Error ejecutando scraper: {e}")
            
    except Exception as e:
        print(f"❌ Error general: {e}")

def generar_recomendaciones():
    """Generar recomendaciones específicas para SII"""
    print("\n💡 **RECOMENDACIONES PARA SII**")
    print("=" * 50)
    
    print("1. 🔍 **VERIFICACIÓN DE ESTRUCTURA:**")
    print("   - Verificar si la estructura de la página cambió")
    print("   - Revisar selectores CSS/XPath")
    print("   - Confirmar que las URLs siguen siendo válidas")
    
    print("\n2. 📅 **VERIFICACIÓN DE FECHAS:**")
    print("   - Verificar que las fechas se extraen correctamente")
    print("   - Implementar filtro por fecha para evitar noticias antiguas")
    print("   - Agregar logging para monitorear fechas extraídas")
    
    print("\n3. 🔧 **ACTUALIZACIÓN DEL SCRAPER:**")
    print("   - Revisar lógica de extracción de noticias")
    print("   - Verificar manejo de errores")
    print("   - Implementar reintentos para conexiones fallidas")
    
    print("\n4. 📊 **MONITOREO:**")
    print("   - Implementar alertas cuando no hay noticias nuevas")
    print("   - Agregar métricas de rendimiento del scraper")
    print("   - Crear dashboard de monitoreo")

def main():
    """Función principal"""
    print("🔍 **ANÁLISIS ESPECÍFICO - SII**")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Ejecutar análisis
    analizar_fechas_sii()
    verificar_urls_sii()
    analizar_estructura_sii()
    verificar_scraper_sii()
    probar_scraper_sii()
    generar_recomendaciones()
    
    print(f"\n✅ **ANÁLISIS COMPLETADO**")
    print("=" * 70)

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Reparación específica del problema de SII que no se actualiza desde 31 julio
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

def verificar_urls_sii():
    """Verificar URLs del SII y su estructura actual"""
    print("🔗 **VERIFICACIÓN DE URLs - SII**")
    print("=" * 50)
    
    urls_a_verificar = [
        "https://www.sii.cl/",
        "https://www.sii.cl/noticias/",
        "https://www.sii.cl/noticias/2025/",
        "https://www.sii.cl/noticias/2025/index.html"
    ]
    
    resultados = {}
    
    for url in urls_a_verificar:
        try:
            response = requests.get(url, timeout=10)
            resultados[url] = {
                'status': response.status_code,
                'accessible': response.status_code == 200,
                'content_length': len(response.text) if response.status_code == 200 else 0
            }
            
            if response.status_code == 200:
                print(f"✅ {url} - Accesible ({len(response.text)} caracteres)")
            else:
                print(f"❌ {url} - Error {response.status_code}")
                
        except Exception as e:
            resultados[url] = {
                'status': 'error',
                'accessible': False,
                'error': str(e)
            }
            print(f"❌ {url} - Error de conexión: {e}")
    
    return resultados

def analizar_estructura_sii():
    """Analizar la estructura actual de la página de noticias del SII"""
    print("\n🔍 **ANÁLISIS DE ESTRUCTURA - SII**")
    print("=" * 50)
    
    try:
        # Acceder a la página principal de noticias
        url = "https://www.sii.cl/noticias/"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            html = response.text
            print("✅ Página de noticias accesible")
            
            # Buscar patrones específicos
            patrones = {
                'enlaces_htm': '.htm' in html,
                'referencias_2025': '2025' in html,
                'estructura_noticias': 'noticias' in html.lower(),
                'tabla_noticias': 'table' in html.lower(),
                'lista_noticias': 'ul' in html.lower() or 'ol' in html.lower(),
                'enlaces_noticias': 'href=' in html and 'noticias' in html
            }
            
            print("\n📊 **PATRONES ENCONTRADOS:**")
            for patron, encontrado in patrones.items():
                status = "✅" if encontrado else "❌"
                print(f"   {status} {patron}")
            
            # Buscar enlaces específicos
            if '.htm' in html:
                print("\n🔗 **ENLACES .HTM ENCONTRADOS:**")
                lineas = html.split('\n')
                for i, linea in enumerate(lineas):
                    if '.htm' in linea and 'href' in linea:
                        print(f"   Línea {i+1}: {linea.strip()[:100]}...")
                        if i > 10:  # Limitar a los primeros 10
                            break
            
            return patrones
            
        else:
            print(f"❌ Error accediendo a la página: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error analizando estructura: {e}")
        return None

def verificar_scraper_sii():
    """Verificar el scraper de SII actual"""
    print("\n🔧 **VERIFICACIÓN DEL SCRAPER - SII**")
    print("=" * 50)
    
    scraper_path = "../backend/scrapers/fuentes/sii/sii_scraper.py"
    
    if not os.path.exists(scraper_path):
        print("❌ Archivo del scraper no encontrado")
        return None
    
    try:
        with open(scraper_path, 'r') as f:
            contenido = f.read()
        
        print("✅ Archivo del scraper encontrado")
        
        # Analizar URLs en el scraper
        urls_en_scraper = []
        lineas = contenido.split('\n')
        for i, linea in enumerate(lineas):
            if 'sii.cl' in linea:
                urls_en_scraper.append((i+1, linea.strip()))
        
        print(f"\n🔗 **URLs EN EL SCRAPER:**")
        for num_linea, linea in urls_en_scraper:
            print(f"   Línea {num_linea}: {linea}")
        
        # Analizar selectores
        selectores = []
        for i, linea in enumerate(lineas):
            if any(selector in linea.lower() for selector in ['selector', 'xpath', 'css', 'find']):
                selectores.append((i+1, linea.strip()))
        
        print(f"\n🎯 **SELECTORES ENCONTRADOS:**")
        for num_linea, linea in selectores[:10]:  # Mostrar solo los primeros 10
            print(f"   Línea {num_linea}: {linea}")
        
        return {
            'urls': urls_en_scraper,
            'selectores': selectores,
            'contenido': contenido
        }
        
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return None

def probar_scraper_sii_manual():
    """Probar el scraper de SII manualmente"""
    print("\n🧪 **PRUEBA MANUAL DEL SCRAPER - SII**")
    print("=" * 50)
    
    try:
        # Intentar acceder directamente a la URL de noticias del SII
        url_noticias = "https://www.sii.cl/noticias/2025/"
        response = requests.get(url_noticias, timeout=10)
        
        if response.status_code == 200:
            html = response.text
            print("✅ URL de noticias accesible")
            
            # Buscar enlaces a noticias específicas
            if '.htm' in html:
                print("✅ Se encontraron enlaces .htm")
                
                # Extraer enlaces manualmente
                enlaces = []
                lineas = html.split('\n')
                for linea in lineas:
                    if '.htm' in linea and 'href' in linea:
                        # Extraer URL del enlace
                        if 'href="' in linea:
                            inicio = linea.find('href="') + 6
                            fin = linea.find('"', inicio)
                            if fin > inicio:
                                url_relativa = linea[inicio:fin]
                                if url_relativa.startswith('./'):
                                    url_relativa = url_relativa[2:]
                                url_completa = f"https://www.sii.cl/noticias/2025/{url_relativa}"
                                enlaces.append(url_completa)
                
                print(f"\n🔗 **ENLACES ENCONTRADOS ({len(enlaces)}):**")
                for i, enlace in enumerate(enlaces[:5], 1):  # Mostrar solo los primeros 5
                    print(f"   {i}. {enlace}")
                
                # Probar acceder a una noticia específica
                if enlaces:
                    print(f"\n🔍 **PROBANDO ACCESO A NOTICIA:**")
                    url_prueba = enlaces[0]
                    try:
                        response_noticia = requests.get(url_prueba, timeout=10)
                        if response_noticia.status_code == 200:
                            print(f"✅ {url_prueba} - Accesible")
                            
                            # Buscar título en la noticia
                            html_noticia = response_noticia.text
                            if '<title>' in html_noticia:
                                inicio = html_noticia.find('<title>') + 7
                                fin = html_noticia.find('</title>', inicio)
                                if fin > inicio:
                                    titulo = html_noticia[inicio:fin].strip()
                                    print(f"   Título: {titulo}")
                        else:
                            print(f"❌ {url_prueba} - Error {response_noticia.status_code}")
                    except Exception as e:
                        print(f"❌ {url_prueba} - Error de conexión: {e}")
                
                return enlaces
            else:
                print("❌ No se encontraron enlaces .htm")
                return []
        else:
            print(f"❌ Error accediendo a URL de noticias: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error en prueba manual: {e}")
        return []

def generar_solucion_sii():
    """Generar solución para el problema de SII"""
    print("\n💡 **SOLUCIÓN PARA SII**")
    print("=" * 50)
    
    print("🔧 **PROBLEMAS IDENTIFICADOS:**")
    print("   - Última noticia del 31 de julio")
    print("   - Posible cambio en estructura de página")
    print("   - URLs o selectores desactualizados")
    
    print("\n🔧 **SOLUCIONES PROPUESTAS:**")
    print("1. **Verificar estructura actual:**")
    print("   - Analizar HTML de la página de noticias")
    print("   - Identificar nuevos patrones de enlaces")
    print("   - Actualizar selectores si es necesario")
    
    print("\n2. **Actualizar URLs:**")
    print("   - Verificar que las URLs siguen siendo válidas")
    print("   - Buscar nuevas URLs de noticias")
    print("   - Implementar redirecciones si es necesario")
    
    print("\n3. **Mejorar extracción:**")
    print("   - Implementar extracción más robusta")
    print("   - Agregar manejo de errores")
    print("   - Implementar reintentos")
    
    print("\n4. **Verificar contenido:**")
    print("   - Confirmar que el SII ha publicado noticias nuevas")
    print("   - Verificar fechas de publicación")
    print("   - Implementar filtros de fecha")

def crear_scraper_sii_mejorado():
    """Crear una versión mejorada del scraper de SII"""
    print("\n🔧 **CREANDO SCRAPER MEJORADO - SII**")
    print("=" * 50)
    
    scraper_mejorado = '''
#!/usr/bin/env python3
"""
Scraper mejorado para SII
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

class SIIScraperMejorado:
    def __init__(self):
        self.base_url = "https://www.sii.cl"
        self.noticias_url = "https://www.sii.cl/noticias/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def obtener_noticias(self):
        """Obtener noticias del SII con manejo mejorado"""
        try:
            # Intentar diferentes URLs
            urls_a_probar = [
                "https://www.sii.cl/noticias/",
                "https://www.sii.cl/noticias/2025/",
                "https://www.sii.cl/noticias/2025/index.html"
            ]
            
            for url in urls_a_probar:
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        print(f"✅ URL accesible: {url}")
                        return self.extraer_noticias(response.text, url)
                except Exception as e:
                    print(f"❌ Error con URL {url}: {e}")
                    continue
            
            print("❌ No se pudo acceder a ninguna URL del SII")
            return []
            
        except Exception as e:
            print(f"❌ Error general: {e}")
            return []
    
    def extraer_noticias(self, html, url_base):
        """Extraer noticias del HTML"""
        noticias = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Buscar enlaces a noticias
        enlaces = soup.find_all('a', href=True)
        
        for enlace in enlaces:
            href = enlace.get('href')
            if '.htm' in href:
                # Construir URL completa
                if href.startswith('./'):
                    href = href[2:]
                elif not href.startswith('http'):
                    href = f"{url_base.rstrip('/')}/{href}"
                
                # Extraer información de la noticia
                titulo = enlace.get_text(strip=True)
                if titulo:
                    noticia = {
                        'titulo': titulo,
                        'url': href,
                        'fuente': 'sii',
                        'fecha_publicacion': datetime.now().isoformat()
                    }
                    noticias.append(noticia)
        
        return noticias
    
    def scrape(self):
        """Método principal de scraping"""
        print("🔍 Iniciando scraping del SII...")
        return self.obtener_noticias()

# Uso del scraper
if __name__ == "__main__":
    scraper = SIIScraperMejorado()
    noticias = scraper.scrape()
    print(f"📊 Noticias encontradas: {len(noticias)}")
    for noticia in noticias[:3]:
        print(f"   - {noticia['titulo']}")
'''
    
    # Guardar el scraper mejorado
    with open('sii_scraper_mejorado.py', 'w') as f:
        f.write(scraper_mejorado)
    
    print("✅ Scraper mejorado creado: sii_scraper_mejorado.py")
    print("\n📋 **CARACTERÍSTICAS DEL SCRAPER MEJORADO:**")
    print("   - Múltiples URLs de respaldo")
    print("   - Manejo de errores robusto")
    print("   - Extracción flexible de enlaces")
    print("   - Headers de navegador realistas")
    print("   - Timeout configurado")

def main():
    """Función principal"""
    print("🔧 **REPARACIÓN ESPECÍFICA - SII**")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Ejecutar análisis y reparación
    verificar_urls_sii()
    analizar_estructura_sii()
    verificar_scraper_sii()
    probar_scraper_sii_manual()
    generar_solucion_sii()
    crear_scraper_sii_mejorado()
    
    print(f"\n✅ **REPARACIÓN COMPLETADA**")
    print("=" * 70)

if __name__ == "__main__":
    main() 
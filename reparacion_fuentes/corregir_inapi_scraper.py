#!/usr/bin/env python3
"""
Corrección del scraper de INAPI basado en la información real
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('../APIS_Y_CREDENCIALES.env')

def analizar_pagina_inapi():
    """Analizar la página real del INAPI"""
    print("🔍 **ANÁLISIS DE LA PÁGINA REAL - INAPI**")
    print("=" * 50)
    
    url = "https://www.inapi.cl/sala-de-prensa/noticias"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            html = response.text
            print("✅ Página del INAPI accesible")
            
            # Buscar enlaces a noticias
            soup = BeautifulSoup(html, 'html.parser')
            
            # Buscar todos los enlaces
            enlaces = soup.find_all('a', href=True)
            
            print(f"\n🔗 **ENLACES ENCONTRADOS ({len(enlaces)}):**")
            enlaces_noticias = []
            
            for enlace in enlaces:
                href = enlace.get('href')
                texto = enlace.get_text(strip=True)
                
                # Filtrar enlaces de noticias
                if 'detalle-noticia' in href and texto:
                    enlaces_noticias.append({
                        'url': href,
                        'texto': texto,
                        'url_completa': f"https://www.inapi.cl{href}" if href.startswith('/') else href
                    })
                    print(f"   📰 {texto[:50]}... -> {href}")
            
            return enlaces_noticias
        else:
            print(f"❌ Error accediendo a la página: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error analizando página: {e}")
        return []

def probar_noticia_inapi_directa():
    """Probar la noticia directa del INAPI"""
    print("\n🧪 **PRUEBA DE NOTICIA DIRECTA - INAPI**")
    print("=" * 50)
    
    url_noticia = "https://www.inapi.cl/sala-de-prensa/detalle-noticia/cuenta-publica-en-talca-inapi-destaca-avances-en-pi-y-anuncia-fortalecimiento-en-regiones"
    
    try:
        response = requests.get(url_noticia, timeout=10)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            print("✅ Noticia del INAPI accesible")
            
            # Extraer título
            titulo = soup.find('h1') or soup.find('title')
            if titulo:
                print(f"📰 Título: {titulo.get_text(strip=True)}")
            
            # Extraer contenido
            contenido = soup.find('body')
            if contenido:
                texto = contenido.get_text(strip=True)
                print(f"📄 Contenido: {texto[:200]}...")
            
            # Buscar fecha
            fecha_pattern = r'(\\w+\\s+\\d{1,2}\\s+\\w+\\s+de\\s+2025)'
            fecha_match = re.search(fecha_pattern, html)
            if fecha_match:
                print(f"📅 Fecha encontrada: {fecha_match.group(1)}")
            
            return True
        else:
            print(f"❌ Error accediendo a la noticia: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando noticia: {e}")
        return False

def crear_scraper_inapi_corregido():
    """Crear un scraper corregido para INAPI"""
    print("\n🔧 **CREANDO SCRAPER CORREGIDO - INAPI**")
    print("=" * 50)
    
    scraper_corregido = '''#!/usr/bin/env python3
"""
Scraper corregido para INAPI basado en la estructura real
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import hashlib

class INAPIScraperCorregido:
    def __init__(self):
        self.base_url = "https://www.inapi.cl"
        self.noticias_url = "https://www.inapi.cl/sala-de-prensa/noticias"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def extraer_noticias_lista(self):
        """Extraer lista de noticias de la página principal"""
        try:
            response = self.session.get(self.noticias_url, timeout=10)
            if response.status_code != 200:
                print(f"❌ Error accediendo a {self.noticias_url}: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            noticias = []
            
            # Buscar enlaces que contengan 'detalle-noticia'
            enlaces = soup.find_all('a', href=True)
            
            for enlace in enlaces:
                href = enlace.get('href')
                texto = enlace.get_text(strip=True)
                
                # Filtrar enlaces de noticias
                if 'detalle-noticia' in href and texto:
                    # Construir URL completa
                    if href.startswith('/'):
                        url_completa = f"{self.base_url}{href}"
                    elif href.startswith('http'):
                        url_completa = href
                    else:
                        url_completa = f"{self.base_url}/{href}"
                    
                    # Extraer información básica
                    noticia = {
                        'url': url_completa,
                        'titulo': texto,
                        'fuente': 'inapi',
                        'fecha_publicacion': datetime.now().isoformat()
                    }
                    
                    # Extraer contenido completo
                    contenido_completo = self.extraer_contenido_noticia(url_completa)
                    if contenido_completo:
                        noticia.update(contenido_completo)
                        noticias.append(noticia)
            
            return noticias
            
        except Exception as e:
            print(f"❌ Error extrayendo lista de noticias: {e}")
            return []
    
    def extraer_contenido_noticia(self, url):
        """Extraer contenido completo de una noticia específica"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraer título
            titulo = soup.find('h1') or soup.find('title')
            titulo_texto = titulo.get_text(strip=True) if titulo else ""
            
            # Extraer contenido
            contenido = ""
            
            # Buscar contenido en diferentes selectores
            selectores_contenido = [
                'article',
                '.contenido',
                '.noticia-contenido',
                'main',
                '.post-content'
            ]
            
            for selector in selectores_contenido:
                contenido_elem = soup.select_one(selector)
                if contenido_elem:
                    # Remover elementos no deseados
                    for elem in contenido_elem.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                        elem.decompose()
                    
                    contenido = contenido_elem.get_text(strip=True)
                    break
            
            # Si no se encuentra con selectores específicos, usar body
            if not contenido:
                body = soup.find('body')
                if body:
                    # Remover elementos no deseados
                    for elem in body.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside', 'menu']):
                        elem.decompose()
                    
                    contenido = body.get_text(strip=True)
            
            # Extraer fecha
            fecha = self.extraer_fecha(soup)
            
            # Generar hash
            hash_contenido = hashlib.md5(f"{titulo_texto}|{contenido[:200]}|{url}".encode('utf-8')).hexdigest()
            
            return {
                'titulo': titulo_texto,
                'contenido': contenido,
                'fecha_publicacion': fecha,
                'hash_contenido': hash_contenido
            }
            
        except Exception as e:
            print(f"❌ Error extrayendo contenido de {url}: {e}")
            return None
    
    def extraer_fecha(self, soup):
        """Extraer fecha de la noticia"""
        try:
            # Buscar fecha en diferentes formatos
            fecha_patterns = [
                r'(\\w+\\s+\\d{1,2}\\s+\\w+\\s+de\\s+2025)',
                r'(\\d{1,2}/\\d{1,2}/2025)',
                r'(\\d{4}-\\d{2}-\\d{2})',
                r'(\\w+\\.\\s+\\d{1,2},\\s+2025)'
            ]
            
            texto_completo = soup.get_text()
            
            for pattern in fecha_patterns:
                match = re.search(pattern, texto_completo)
                if match:
                    return match.group(1)
            
            # Si no se encuentra, usar fecha actual
            return datetime.now().isoformat()
            
        except Exception as e:
            print(f"❌ Error extrayendo fecha: {e}")
            return datetime.now().isoformat()
    
    def scrape(self):
        """Método principal de scraping"""
        print("🔍 Iniciando scraping del INAPI (versión corregida)...")
        noticias = self.extraer_noticias_lista()
        print(f"✅ Se extrajeron {len(noticias)} noticias del INAPI")
        return noticias

# Uso del scraper
if __name__ == "__main__":
    scraper = INAPIScraperCorregido()
    noticias = scraper.scrape()
    for noticia in noticias[:3]:
        print(f"   📰 {noticia['titulo'][:50]}...")
'''
    
    # Guardar el scraper corregido
    with open('inapi_scraper_corregido.py', 'w') as f:
        f.write(scraper_corregido)
    
    print("✅ Scraper corregido creado: inapi_scraper_corregido.py")
    print("\n📋 **MEJORAS IMPLEMENTADAS:**")
    print("   - Extracción correcta de enlaces 'detalle-noticia'")
    print("   - Manejo de URLs relativas y absolutas")
    print("   - Extracción de contenido completo")
    print("   - Detección de fechas mejorada")
    print("   - Generación de hash único")

def probar_scraper_corregido():
    """Probar el scraper corregido"""
    print("\n🧪 **PRUEBA DEL SCRAPER CORREGIDO**")
    print("=" * 50)
    
    try:
        # Importar y ejecutar el scraper corregido
        from inapi_scraper_corregido import INAPIScraperCorregido
        
        scraper = INAPIScraperCorregido()
        noticias = scraper.scrape()
        
        if noticias:
            print(f"✅ Se extrajeron {len(noticias)} noticias")
            
            for i, noticia in enumerate(noticias[:3], 1):
                titulo = noticia.get('titulo', 'Sin título')
                fecha = noticia.get('fecha_publicacion', 'Sin fecha')
                print(f"   {i}. {titulo[:50]}... ({fecha[:10]})")
        else:
            print("❌ No se extrajeron noticias")
            
    except ImportError:
        print("⚠️ Scraper corregido no disponible, creando...")
        crear_scraper_inapi_corregido()
    except Exception as e:
        print(f"❌ Error probando scraper: {e}")

def main():
    """Función principal"""
    print("🔧 **CORRECCIÓN DEL SCRAPER - INAPI**")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Ejecutar análisis y corrección
    analizar_pagina_inapi()
    probar_noticia_inapi_directa()
    crear_scraper_inapi_corregido()
    probar_scraper_corregido()
    
    print(f"\n✅ **CORRECCIÓN COMPLETADA**")
    print("=" * 70)

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Corrección del scraper de SII basado en la información real
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

def analizar_pagina_sii():
    """Analizar la página real del SII"""
    print("🔍 **ANÁLISIS DE LA PÁGINA REAL - SII**")
    print("=" * 50)
    
    url = "https://www.sii.cl/noticias/2025/index.html"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            html = response.text
            print("✅ Página del SII accesible")
            
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
                if '.htm' in href and any(palabra in texto.lower() for palabra in ['noticia', '2025', 'julio', 'junio']):
                    enlaces_noticias.append({
                        'url': href,
                        'texto': texto,
                        'url_completa': f"https://www.sii.cl/noticias/2025/{href}" if not href.startswith('http') else href
                    })
                    print(f"   📰 {texto[:50]}... -> {href}")
            
            return enlaces_noticias
        else:
            print(f"❌ Error accediendo a la página: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error analizando página: {e}")
        return []

def probar_noticia_sii_directa():
    """Probar la noticia directa del SII"""
    print("\n🧪 **PRUEBA DE NOTICIA DIRECTA - SII**")
    print("=" * 50)
    
    url_noticia = "https://www.sii.cl/noticias/2025/310725noti01pcr.htm"
    
    try:
        response = requests.get(url_noticia, timeout=10)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            print("✅ Noticia del SII accesible")
            
            # Extraer título
            titulo = soup.find('title')
            if titulo:
                print(f"📰 Título: {titulo.get_text(strip=True)}")
            
            # Extraer contenido
            contenido = soup.find('body')
            if contenido:
                texto = contenido.get_text(strip=True)
                print(f"📄 Contenido: {texto[:200]}...")
            
            # Buscar fecha
            fecha_pattern = r'(\d{1,2}\s+de\s+\w+\s+de\s+2025)'
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

def crear_scraper_sii_corregido():
    """Crear un scraper corregido para SII"""
    print("\n🔧 **CREANDO SCRAPER CORREGIDO - SII**")
    print("=" * 50)
    
    scraper_corregido = '''#!/usr/bin/env python3
"""
Scraper corregido para SII basado en la estructura real
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import hashlib

class SIIScraperCorregido:
    def __init__(self):
        self.base_url = "https://www.sii.cl"
        self.noticias_url = "https://www.sii.cl/noticias/2025/index.html"
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
            
            # Buscar enlaces que contengan .htm
            enlaces = soup.find_all('a', href=True)
            
            for enlace in enlaces:
                href = enlace.get('href')
                texto = enlace.get_text(strip=True)
                
                # Filtrar enlaces de noticias
                if '.htm' in href and texto:
                    # Construir URL completa
                    if href.startswith('./'):
                        href = href[2:]
                    elif not href.startswith('http'):
                        href = f"https://www.sii.cl/noticias/2025/{href}"
                    
                    # Extraer información básica
                    noticia = {
                        'url': href,
                        'titulo': texto,
                        'fuente': 'sii',
                        'fecha_publicacion': datetime.now().isoformat()
                    }
                    
                    # Extraer contenido completo
                    contenido_completo = self.extraer_contenido_noticia(href)
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
            titulo = soup.find('title')
            titulo_texto = titulo.get_text(strip=True) if titulo else ""
            
            # Extraer contenido
            contenido = ""
            body = soup.find('body')
            if body:
                # Remover elementos no deseados
                for elem in body.find_all(['script', 'style', 'nav', 'header', 'footer']):
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
                r'(\\d{1,2}\\s+de\\s+\\w+\\s+de\\s+2025)',
                r'(\\d{1,2}/\\d{1,2}/2025)',
                r'(\\d{4}-\\d{2}-\\d{2})'
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
        print("🔍 Iniciando scraping del SII (versión corregida)...")
        noticias = self.extraer_noticias_lista()
        print(f"✅ Se extrajeron {len(noticias)} noticias del SII")
        return noticias

# Uso del scraper
if __name__ == "__main__":
    scraper = SIIScraperCorregido()
    noticias = scraper.scrape()
    for noticia in noticias[:3]:
        print(f"   📰 {noticia['titulo'][:50]}...")
'''
    
    # Guardar el scraper corregido
    with open('sii_scraper_corregido.py', 'w') as f:
        f.write(scraper_corregido)
    
    print("✅ Scraper corregido creado: sii_scraper_corregido.py")
    print("\n📋 **MEJORAS IMPLEMENTADAS:**")
    print("   - Extracción correcta de enlaces .htm")
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
        from sii_scraper_corregido import SIIScraperCorregido
        
        scraper = SIIScraperCorregido()
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
        crear_scraper_sii_corregido()
    except Exception as e:
        print(f"❌ Error probando scraper: {e}")

def main():
    """Función principal"""
    print("🔧 **CORRECCIÓN DEL SCRAPER - SII**")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Ejecutar análisis y corrección
    analizar_pagina_sii()
    probar_noticia_sii_directa()
    crear_scraper_sii_corregido()
    probar_scraper_corregido()
    
    print(f"\n✅ **CORRECCIÓN COMPLETADA**")
    print("=" * 70)

if __name__ == "__main__":
    main() 
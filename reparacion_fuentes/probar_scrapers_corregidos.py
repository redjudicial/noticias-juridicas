#!/usr/bin/env python3
"""
Probar los scrapers corregidos de SII e INAPI
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

# Configuración de Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://qfomiierchksyfhxoukj.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def probar_sii_manual():
    """Probar SII manualmente para entender la estructura"""
    print("🧪 **PRUEBA MANUAL - SII**")
    print("=" * 50)
    
    url = "https://www.sii.cl/noticias/2025/index.html"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            print("✅ Página del SII accesible")
            
            # Buscar enlaces específicos
            enlaces = soup.find_all('a', href=True)
            
            print(f"\n🔍 **BUSCANDO ENLACES ESPECÍFICOS:**")
            enlaces_noticias = []
            
            for enlace in enlaces:
                href = enlace.get('href')
                texto = enlace.get_text(strip=True)
                
                # Buscar enlaces que contengan códigos de noticias
                if '.htm' in href and any(char.isdigit() for char in href):
                    enlaces_noticias.append({
                        'url': href,
                        'texto': texto,
                        'url_completa': f"https://www.sii.cl/noticias/2025/{href}" if not href.startswith('http') else href
                    })
                    print(f"   📰 {texto[:30]}... -> {href}")
            
            # Probar acceder a una noticia específica
            if enlaces_noticias:
                print(f"\n🔍 **PROBANDO NOTICIA ESPECÍFICA:**")
                noticia_prueba = enlaces_noticias[0]
                
                try:
                    response_noticia = requests.get(noticia_prueba['url_completa'], timeout=10)
                    if response_noticia.status_code == 200:
                        print(f"✅ {noticia_prueba['url_completa']} - Accesible")
                        
                        # Extraer información básica
                        soup_noticia = BeautifulSoup(response_noticia.text, 'html.parser')
                        
                        # Buscar título
                        titulo = soup_noticia.find('title')
                        if titulo:
                            print(f"   📰 Título: {titulo.get_text(strip=True)}")
                        
                        # Buscar fecha
                        fecha_pattern = r'(\d{1,2}\s+de\s+\w+\s+de\s+2025)'
                        fecha_match = re.search(fecha_pattern, response_noticia.text)
                        if fecha_match:
                            print(f"   📅 Fecha: {fecha_match.group(1)}")
                        
                        return True
                    else:
                        print(f"❌ {noticia_prueba['url_completa']} - Error {response_noticia.status_code}")
                        return False
                        
                except Exception as e:
                    print(f"❌ Error accediendo a noticia: {e}")
                    return False
            else:
                print("❌ No se encontraron enlaces de noticias")
                return False
                
        else:
            print(f"❌ Error accediendo a la página: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba manual: {e}")
        return False

def probar_inapi_manual():
    """Probar INAPI manualmente"""
    print("\n🧪 **PRUEBA MANUAL - INAPI**")
    print("=" * 50)
    
    url = "https://www.inapi.cl/sala-de-prensa/noticias"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            print("✅ Página del INAPI accesible")
            
            # Buscar enlaces de noticias
            enlaces = soup.find_all('a', href=True)
            
            print(f"\n🔍 **BUSCANDO ENLACES DE NOTICIAS:**")
            enlaces_noticias = []
            
            for enlace in enlaces:
                href = enlace.get('href')
                texto = enlace.get_text(strip=True)
                
                # Filtrar enlaces de noticias
                if 'detalle-noticia' in href and texto and len(texto) > 10:
                    enlaces_noticias.append({
                        'url': href,
                        'texto': texto,
                        'url_completa': f"https://www.inapi.cl{href}" if href.startswith('/') else href
                    })
                    print(f"   📰 {texto[:50]}... -> {href}")
            
            # Probar acceder a una noticia específica
            if enlaces_noticias:
                print(f"\n🔍 **PROBANDO NOTICIA ESPECÍFICA:**")
                noticia_prueba = enlaces_noticias[0]
                
                try:
                    response_noticia = requests.get(noticia_prueba['url_completa'], timeout=10)
                    if response_noticia.status_code == 200:
                        print(f"✅ {noticia_prueba['url_completa']} - Accesible")
                        
                        # Extraer información básica
                        soup_noticia = BeautifulSoup(response_noticia.text, 'html.parser')
                        
                        # Buscar título
                        titulo = soup_noticia.find('h1') or soup_noticia.find('title')
                        if titulo:
                            print(f"   📰 Título: {titulo.get_text(strip=True)}")
                        
                        # Buscar fecha
                        fecha_pattern = r'(\w+\s+\d{1,2}\s+\w+\s+de\s+2025)'
                        fecha_match = re.search(fecha_pattern, response_noticia.text)
                        if fecha_match:
                            print(f"   📅 Fecha: {fecha_match.group(1)}")
                        
                        return True
                    else:
                        print(f"❌ {noticia_prueba['url_completa']} - Error {response_noticia.status_code}")
                        return False
                        
                except Exception as e:
                    print(f"❌ Error accediendo a noticia: {e}")
                    return False
            else:
                print("❌ No se encontraron enlaces de noticias")
                return False
                
        else:
            print(f"❌ Error accediendo a la página: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba manual: {e}")
        return False

def crear_scraper_sii_final():
    """Crear scraper final para SII basado en el análisis manual"""
    print("\n🔧 **CREANDO SCRAPER FINAL - SII**")
    print("=" * 50)
    
    scraper_final = '''#!/usr/bin/env python3
"""
Scraper final para SII basado en análisis manual
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import hashlib

class SIIScraperFinal:
    def __init__(self):
        self.base_url = "https://www.sii.cl"
        self.noticias_url = "https://www.sii.cl/noticias/2025/index.html"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def extraer_codigos_noticias(self):
        """Extraer códigos de noticias de la página principal"""
        try:
            response = self.session.get(self.noticias_url, timeout=10)
            if response.status_code != 200:
                print(f"❌ Error accediendo a {self.noticias_url}: {response.status_code}")
                return []
            
            # Buscar códigos de noticias en el HTML
            html = response.text
            
            # Patrón para encontrar códigos de noticias (ej: 310725noti01pcr)
            codigos_pattern = r'([0-9]{6}noti[0-9]{2}[a-z]{3})'
            codigos = re.findall(codigos_pattern, html)
            
            print(f"🔍 Encontrados {len(codigos)} códigos de noticias")
            
            noticias = []
            for codigo in codigos[:10]:  # Limitar a 10 noticias
                url_noticia = f"https://www.sii.cl/noticias/2025/{codigo}.htm"
                noticia = self.extraer_noticia_por_codigo(url_noticia, codigo)
                if noticia:
                    noticias.append(noticia)
            
            return noticias
            
        except Exception as e:
            print(f"❌ Error extrayendo códigos: {e}")
            return []
    
    def extraer_noticia_por_codigo(self, url, codigo):
        """Extraer noticia específica por código"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraer título
            titulo = soup.find('title')
            titulo_texto = titulo.get_text(strip=True) if titulo else f"Noticia SII {codigo}"
            
            # Extraer contenido
            contenido = ""
            body = soup.find('body')
            if body:
                # Remover elementos no deseados
                for elem in body.find_all(['script', 'style', 'nav', 'header', 'footer']):
                    elem.decompose()
                
                contenido = body.get_text(strip=True)
            
            # Extraer fecha
            fecha = self.extraer_fecha_sii(soup)
            
            # Generar hash
            hash_contenido = hashlib.md5(f"{titulo_texto}|{contenido[:200]}|{url}".encode('utf-8')).hexdigest()
            
            return {
                'titulo': titulo_texto,
                'contenido': contenido,
                'url_origen': url,
                'fuente': 'sii',
                'fecha_publicacion': fecha,
                'hash_contenido': hash_contenido
            }
            
        except Exception as e:
            print(f"❌ Error extrayendo noticia {codigo}: {e}")
            return None
    
    def extraer_fecha_sii(self, soup):
        """Extraer fecha específica del SII"""
        try:
            texto_completo = soup.get_text()
            
            # Patrón específico del SII
            fecha_pattern = r'(\\d{1,2}\\s+de\\s+\\w+\\s+de\\s+2025)'
            match = re.search(fecha_pattern, texto_completo)
            
            if match:
                return match.group(1)
            
            return datetime.now().isoformat()
            
        except Exception as e:
            return datetime.now().isoformat()
    
    def scrape(self):
        """Método principal de scraping"""
        print("🔍 Iniciando scraping del SII (versión final)...")
        noticias = self.extraer_codigos_noticias()
        print(f"✅ Se extrajeron {len(noticias)} noticias del SII")
        return noticias

# Uso del scraper
if __name__ == "__main__":
    scraper = SIIScraperFinal()
    noticias = scraper.scrape()
    for noticia in noticias[:3]:
        print(f"   📰 {noticia['titulo'][:50]}...")
'''
    
    # Guardar el scraper final
    with open('sii_scraper_final.py', 'w') as f:
        f.write(scraper_final)
    
    print("✅ Scraper final creado: sii_scraper_final.py")

def probar_scrapers_finales():
    """Probar los scrapers finales"""
    print("\n🧪 **PRUEBA DE SCRAPERS FINALES**")
    print("=" * 50)
    
    # Probar SII
    try:
        from sii_scraper_final import SIIScraperFinal
        scraper_sii = SIIScraperFinal()
        noticias_sii = scraper_sii.scrape()
        print(f"✅ SII: {len(noticias_sii)} noticias extraídas")
        
        for i, noticia in enumerate(noticias_sii[:2], 1):
            titulo = noticia.get('titulo', 'Sin título')
            fecha = noticia.get('fecha_publicacion', 'Sin fecha')
            print(f"   {i}. {titulo[:50]}... ({fecha[:10]})")
            
    except Exception as e:
        print(f"❌ Error probando SII: {e}")
    
    # Probar INAPI
    try:
        from inapi_scraper_corregido import INAPIScraperCorregido
        scraper_inapi = INAPIScraperCorregido()
        noticias_inapi = scraper_inapi.scrape()
        print(f"✅ INAPI: {len(noticias_inapi)} noticias extraídas")
        
        for i, noticia in enumerate(noticias_inapi[:2], 1):
            titulo = noticia.get('titulo', 'Sin título')
            fecha = noticia.get('fecha_publicacion', 'Sin fecha')
            print(f"   {i}. {titulo[:50]}... ({fecha[:10]})")
            
    except Exception as e:
        print(f"❌ Error probando INAPI: {e}")

def main():
    """Función principal"""
    print("🧪 **PRUEBA DE SCRAPERS CORREGIDOS**")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Ejecutar pruebas
    probar_sii_manual()
    probar_inapi_manual()
    crear_scraper_sii_final()
    probar_scrapers_finales()
    
    print(f"\n✅ **PRUEBAS COMPLETADAS**")
    print("=" * 70)

if __name__ == "__main__":
    main() 
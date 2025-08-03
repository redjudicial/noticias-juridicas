#!/usr/bin/env python3
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
                r'(\d{1,2}\s+de\s+\w+\s+de\s+2025)',
                r'(\d{1,2}/\d{1,2}/2025)',
                r'(\d{4}-\d{2}-\d{2})'
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

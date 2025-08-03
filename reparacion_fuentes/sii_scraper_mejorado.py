
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

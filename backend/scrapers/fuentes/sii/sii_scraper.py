#!/usr/bin/env python3
"""
Scraper final para SII basado en análisis manual
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timezone
import hashlib
from typing import List, Optional
from ..data_schema import NoticiaEstandarizada, Categoria, Jurisdiccion, TipoDocumento
from ..date_extractor import date_extractor

class SIIScraper:
    def __init__(self, openai_api_key: str = None):
        self.base_url = "https://www.sii.cl"
        self.noticias_url = "https://www.sii.cl/noticias/2025/index.html"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.openai_api_key = openai_api_key
    
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
            fecha = self._extract_fecha_universal(soup, url)
            
            # Generar hash
            hash_contenido = hashlib.md5(f"{titulo_texto}|{contenido[:200]}|{url}".encode('utf-8')).hexdigest()
            
            return NoticiaEstandarizada(
                titulo=titulo_texto,
                cuerpo_completo=contenido,
                fecha_publicacion=fecha,
                fuente='sii',
                url_origen=url,
                categoria=Categoria.ORGANISMO,
                jurisdiccion=Jurisdiccion.NACIONAL,
                tipo_documento=TipoDocumento.NOTICIA,
                hash_contenido=hash_contenido
            )
            
        except Exception as e:
            print(f"❌ Error extrayendo noticia {codigo}: {e}")
            return None
    
    def _extract_fecha_universal(self, soup: BeautifulSoup, url: str = None) -> datetime:
        """Extraer fecha usando extractor universal"""
        try:
            fecha = date_extractor.extract_date_from_html(soup, url)
            if fecha:
                return fecha
            return datetime.now(timezone.utc)
        except Exception as e:
            print(f"⚠️ Error extrayendo fecha: {e}")
            return datetime.now(timezone.utc)
    
    def scrape(self):
        """Método principal de scraping"""
        print("🔍 Iniciando scraping del SII (versión final)...")
        noticias = self.extraer_codigos_noticias()
        print(f"✅ Se extrajeron {len(noticias)} noticias del SII")
        return noticias
    
    def scrape_noticias_recientes(self, max_noticias: int = 10) -> List[NoticiaEstandarizada]:
        """Método compatible con el sistema principal"""
        return self.scrape()

# Uso del scraper
if __name__ == "__main__":
    scraper = SIIScraper()
    noticias = scraper.scrape()
    for noticia in noticias[:3]:
        print(f"   📰 {noticia['titulo'][:50]}...")

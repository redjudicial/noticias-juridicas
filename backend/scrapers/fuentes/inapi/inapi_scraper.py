#!/usr/bin/env python3
"""
Scraper corregido para INAPI basado en la estructura real
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import hashlib
from typing import List, Optional
from ..data_schema import NoticiaEstandarizada, Categoria, Jurisdiccion, TipoDocumento
import hashlib

class INAPIScraper:
    def __init__(self, openai_api_key: str = None):
        self.base_url = "https://www.inapi.cl"
        self.noticias_url = "https://www.inapi.cl/sala-de-prensa/noticias"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.openai_api_key = openai_api_key
    
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
                    noticia = NoticiaEstandarizada(
                        titulo=texto,
                        cuerpo_completo=texto,  # Por ahora usamos el título como contenido
                        fecha_publicacion=datetime.now().replace(tzinfo=None),
                        fuente='inapi',
                        url_origen=url_completa,
                        categoria=Categoria.ORGANISMO,
                        jurisdiccion=Jurisdiccion.NACIONAL,
                        tipo_documento=TipoDocumento.NOTICIA
                    )
                    
                    # Extraer contenido completo
                    contenido_completo = self.extraer_contenido_noticia(url_completa)
                    if contenido_completo:
                        # Usar el contenido completo en lugar del básico
                        noticias.append(contenido_completo)
                    else:
                        # Si no se puede extraer contenido completo, usar el básico
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
            
            return NoticiaEstandarizada(
                titulo=titulo_texto,
                cuerpo_completo=contenido,
                fecha_publicacion=fecha,
                fuente='inapi',
                url_origen=url,
                categoria=Categoria.ORGANISMO,
                jurisdiccion=Jurisdiccion.NACIONAL,
                tipo_documento=TipoDocumento.NOTICIA,
                hash_contenido=hash_contenido
            )
            
        except Exception as e:
            print(f"❌ Error extrayendo contenido de {url}: {e}")
            return None
    
    def extraer_fecha(self, soup):
        """Extraer fecha de la noticia"""
        try:
            # Buscar fecha en diferentes formatos
            fecha_patterns = [
                r'(\w+\s+\d{1,2}\s+\w+\s+de\s+2025)',
                r'(\d{1,2}/\d{1,2}/2025)',
                r'(\d{4}-\d{2}-\d{2})',
                r'(\w+\.\s+\d{1,2},\s+2025)'
            ]
            
            texto_completo = soup.get_text()
            
            for pattern in fecha_patterns:
                match = re.search(pattern, texto_completo)
                if match:
                    fecha_str = match.group(1)
                    
                    # Intentar parsear diferentes formatos
                    try:
                        # Formato: "31 de julio de 2025"
                        if ' de ' in fecha_str:
                            meses = {
                                'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
                                'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
                                'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
                            }
                            partes = fecha_str.split(' de ')
                            if len(partes) == 3:
                                dia = int(partes[0])
                                mes = meses.get(partes[1].lower(), 1)
                                año = int(partes[2])
                                return datetime(año, mes, dia).replace(tzinfo=None)
                        
                        # Formato: "31/07/2025"
                        elif '/' in fecha_str:
                            return datetime.strptime(fecha_str, '%d/%m/%Y').replace(tzinfo=None)
                        
                        # Formato: "2025-07-31"
                        elif '-' in fecha_str:
                            return datetime.strptime(fecha_str, '%Y-%m-%d').replace(tzinfo=None)
                        
                        # Formato: "Jul. 31, 2025"
                        elif ',' in fecha_str:
                            return datetime.strptime(fecha_str, '%b. %d, %Y').replace(tzinfo=None)
                            
                    except ValueError:
                        pass
            
            # Si no se encuentra, usar fecha actual
            return datetime.now().replace(tzinfo=None)
            
        except Exception as e:
            print(f"❌ Error extrayendo fecha: {e}")
            return datetime.now().replace(tzinfo=None)
    
    def scrape(self):
        """Método principal de scraping"""
        print("🔍 Iniciando scraping del INAPI (versión corregida)...")
        noticias = self.extraer_noticias_lista()
        print(f"✅ Se extrajeron {len(noticias)} noticias del INAPI")
        return noticias
    
    def scrape_noticias_recientes(self, max_noticias: int = 10) -> List[NoticiaEstandarizada]:
        """Método compatible con el sistema principal"""
        return self.scrape()

# Uso del scraper
if __name__ == "__main__":
    scraper = INAPIScraperCorregido()
    noticias = scraper.scrape()
    for noticia in noticias[:3]:
        print(f"   📰 {noticia['titulo'][:50]}...")

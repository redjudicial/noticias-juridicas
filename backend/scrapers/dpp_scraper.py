#!/usr/bin/env python3
"""
Scraper para la Defensoría Penal Pública de Chile
Extrae noticias completas de https://www.dpp.cl
"""

import os
import sys
import requests
import time
from datetime import datetime, timezone
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.processors.content_processor import ContentProcessor, NoticiaCompleta

class DPPScraper:
    """Scraper para la Defensoría Penal Pública de Chile"""
    
    def __init__(self, openai_api_key: str = None):
        self.base_url = "https://www.dpp.cl"
        self.noticias_url = "https://www.dpp.cl/sala_prensa/noticias"
        self.content_processor = ContentProcessor(openai_api_key or "")
        
        # Configurar sesión
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_noticias_recientes(self, max_noticias: int = 20) -> List[Dict]:
        """Obtener lista de noticias recientes"""
        try:
            print(f"🔍 Obteniendo noticias de la Defensoría Penal Pública...")
            
            response = self.session.get(self.noticias_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar contenedor de noticias
            noticias_container = soup.find('div', class_='noticias') or soup.find('main') or soup.find('body')
            
            if not noticias_container:
                print("❌ No se encontró contenedor de noticias")
                return []
            
            # Buscar enlaces de noticias
            noticias_links = []
            
            # Buscar enlaces en diferentes formatos
            for link in noticias_container.find_all('a', href=True):
                href = link.get('href')
                if href and self._is_noticia_link(href):
                    titulo = link.get_text(strip=True)
                    if titulo and len(titulo) > 10:  # Filtrar títulos muy cortos
                        noticias_links.append({
                            'titulo': titulo,
                            'url': urljoin(self.base_url, href),
                            'fecha': self._extract_fecha_link(link)
                        })
            
            # Ordenar por fecha y limitar
            noticias_links = sorted(noticias_links, key=lambda x: x['fecha'] or datetime.now(), reverse=True)
            noticias_links = noticias_links[:max_noticias]
            
            print(f"✅ Encontradas {len(noticias_links)} noticias")
            return noticias_links
            
        except Exception as e:
            print(f"❌ Error obteniendo noticias: {e}")
            return []
    
    def get_noticia_completa(self, url: str, titulo: str = None) -> Optional[NoticiaCompleta]:
        """Obtener noticia completa desde una URL"""
        try:
            print(f"📄 Extrayendo noticia: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer información específica de la DPP
            noticia = self._extract_noticia_dpp(soup, url, titulo)
            
            if noticia:
                print(f"✅ Noticia extraída: {noticia.titulo[:50]}...")
            
            return noticia
            
        except Exception as e:
            print(f"❌ Error extrayendo noticia: {e}")
            return None
    
    def _extract_noticia_dpp(self, soup: BeautifulSoup, url: str, titulo: str = None) -> Optional[NoticiaCompleta]:
        """Extraer noticia específica de la DPP"""
        try:
            # Extraer título
            titulo_elem = soup.find('h1') or soup.find('h2') or soup.find('title')
            titulo_final = titulo or (titulo_elem.get_text(strip=True) if titulo_elem else "Noticia Defensoría Penal Pública")
            
            # Extraer fecha
            fecha = self._extract_fecha_dpp(soup)
            
            # Extraer contenido
            contenido = self._extract_contenido_dpp(soup)
            
            if not contenido:
                return None
            
            # Crear objeto NoticiaCompleta
            noticia = NoticiaCompleta(
                titulo=titulo_final,
                titulo_original=titulo_final,
                cuerpo_completo=contenido,
                fecha_publicacion=fecha,
                fuente='dpp',
                fuente_nombre_completo='Defensoría Penal Pública',
                url_origen=url,
                categoria='penal',
                tipo_documento='noticia',
                jurisdiccion='penal'
            )
            
            return noticia
            
        except Exception as e:
            print(f"❌ Error extrayendo noticia de la DPP: {e}")
            return None
    
    def _extract_fecha_dpp(self, soup: BeautifulSoup) -> datetime:
        """Extraer fecha de noticia de la DPP"""
        try:
            # Buscar fecha en diferentes formatos
            fecha_selectors = [
                '.fecha', '.date', '.fecha-publicacion',
                'time', '[datetime]', '.meta .fecha'
            ]
            
            for selector in fecha_selectors:
                fecha_elem = soup.select_one(selector)
                if fecha_elem:
                    fecha_texto = fecha_elem.get_text(strip=True)
                    fecha_parsed = self._parse_fecha_dpp(fecha_texto)
                    if fecha_parsed:
                        return fecha_parsed
            
            # Si no se encuentra, usar fecha actual
            return datetime.now(timezone.utc)
            
        except Exception as e:
            print(f"⚠️  Error extrayendo fecha: {e}")
            return datetime.now(timezone.utc)
    
    def _parse_fecha_dpp(self, fecha_texto: str) -> Optional[datetime]:
        """Parsear fecha de la DPP"""
        try:
            # Patrones de fecha comunes en la DPP
            patrones = [
                r'(\d{1,2})/(\d{1,2})/(\d{4})',
                r'(\d{1,2})-(\d{1,2})-(\d{4})',
                r'(\d{4})-(\d{1,2})-(\d{1,2})',
                r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})'
            ]
            
            for patron in patrones:
                match = re.search(patron, fecha_texto)
                if match:
                    if len(match.groups()) == 3:
                        if patron == r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})':
                            # Formato: "15 de julio de 2024"
                            dia = int(match.group(1))
                            mes_texto = match.group(2).lower()
                            año = int(match.group(3))
                            
                            meses = {
                                'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
                                'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
                                'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
                            }
                            
                            if mes_texto in meses:
                                return datetime(año, meses[mes_texto], dia, tzinfo=timezone.utc)
                        else:
                            # Formato numérico
                            if patron == r'(\d{4})-(\d{1,2})-(\d{1,2})':
                                año, mes, dia = match.groups()
                            else:
                                dia, mes, año = match.groups()
                            
                            return datetime(int(año), int(mes), int(dia), tzinfo=timezone.utc)
            
            return None
            
        except Exception as e:
            print(f"⚠️  Error parseando fecha: {e}")
            return None
    
    def _extract_contenido_dpp(self, soup: BeautifulSoup) -> str:
        """Extraer contenido de noticia de la DPP"""
        try:
            # Buscar contenido en diferentes selectors
            contenido_selectors = [
                '.contenido', '.content', '.noticia-contenido',
                '.post-content', '.entry-content', 'article',
                '.noticia-texto', '.texto-noticia'
            ]
            
            for selector in contenido_selectors:
                contenido_elem = soup.select_one(selector)
                if contenido_elem:
                    return self._limpiar_contenido(contenido_elem)
            
            # Si no se encuentra, buscar en el body
            body = soup.find('body')
            if body:
                # Remover elementos no deseados
                for elem in body.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                    elem.decompose()
                
                return self._limpiar_contenido(body)
            
            return ""
            
        except Exception as e:
            print(f"❌ Error extrayendo contenido: {e}")
            return ""
    
    def _limpiar_contenido(self, elemento) -> str:
        """Limpiar contenido HTML"""
        try:
            # Remover scripts y estilos
            for script in elemento(["script", "style"]):
                script.decompose()
            
            # Obtener texto
            texto = elemento.get_text(separator=' ', strip=True)
            
            # Limpiar espacios extra
            texto = re.sub(r'\s+', ' ', texto)
            texto = texto.strip()
            
            return texto
            
        except Exception as e:
            print(f"⚠️  Error limpiando contenido: {e}")
            return ""
    
    def _is_noticia_link(self, href: str) -> bool:
        """Verificar si un enlace es de noticia"""
        try:
            # Patrones de URLs de noticias de la DPP
            patrones = [
                r'/noticias/',
                r'/sala-de-prensa/',
                r'/comunicados/',
                r'/prensa/'
            ]
            
            for patron in patrones:
                if re.search(patron, href, re.IGNORECASE):
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _extract_fecha_link(self, link_elem) -> Optional[datetime]:
        """Extraer fecha de un enlace"""
        try:
            # Buscar fecha en el texto del enlace o elementos cercanos
            fecha_texto = link_elem.get_text(strip=True)
            return self._parse_fecha_dpp(fecha_texto)
        except Exception:
            return None
    
    def scrape_noticias_recientes(self, max_noticias: int = 10) -> List[NoticiaCompleta]:
        """Scraper completo de noticias recientes"""
        try:
            print(f"🚀 Iniciando scraping de la Defensoría Penal Pública...")
            
            # Obtener lista de noticias
            noticias_links = self.get_noticias_recientes(max_noticias)
            
            if not noticias_links:
                print("❌ No se encontraron noticias")
                return []
            
            # Extraer noticias completas
            noticias_completas = []
            
            for i, noticia_link in enumerate(noticias_links, 1):
                print(f"📄 Procesando noticia {i}/{len(noticias_links)}: {noticia_link['titulo'][:50]}...")
                
                noticia_completa = self.get_noticia_completa(
                    noticia_link['url'],
                    noticia_link['titulo']
                )
                
                if noticia_completa:
                    noticias_completas.append(noticia_completa)
                
                # Pausa entre requests
                time.sleep(1)
            
            print(f"✅ Scraping completado: {len(noticias_completas)} noticias extraídas")
            return noticias_completas
            
        except Exception as e:
            print(f"❌ Error en scraping: {e}")
            return []

def test_scraper():
    """Función de prueba"""
    scraper = DPPScraper()
    noticias = scraper.scrape_noticias_recientes(3)
    
    for noticia in noticias:
        print(f"📰 {noticia.titulo}")
        print(f"   URL: {noticia.url_origen}")
        print(f"   Fecha: {noticia.fecha_publicacion}")
        print(f"   Contenido: {len(noticia.cuerpo_completo)} caracteres")
        print("---")

if __name__ == "__main__":
    test_scraper() 
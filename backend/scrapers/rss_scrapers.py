#!/usr/bin/env python3
"""
Scrapers para fuentes RSS de noticias jurídicas
Incluye: Ministerio de Justicia, Fiscalía, Contraloría, CDE
"""

import os
import sys
import requests
import time
import feedparser
from datetime import datetime, timezone
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.processors.content_processor import ContentProcessor, NoticiaCompleta

class RSSScraper:
    """Clase base para scrapers RSS"""
    
    def __init__(self, openai_api_key: str = None):
        self.content_processor = ContentProcessor(openai_api_key or "")
        
        # Configurar sesión
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def get_noticias_from_rss(self, rss_url: str, max_noticias: int = 20) -> List[Dict]:
        """Obtener noticias desde un feed RSS"""
        try:
            print(f"🔍 Obteniendo noticias desde RSS: {rss_url}")
            
            # Parsear RSS feed
            feed = feedparser.parse(rss_url)
            
            if not feed.entries:
                print("❌ No se encontraron entradas en el RSS")
                return []
            
            noticias = []
            
            for entry in feed.entries[:max_noticias]:
                try:
                    # Extraer información básica
                    titulo = entry.get('title', '')
                    link = entry.get('link', '')
                    
                    # Extraer fecha
                    fecha = self._extract_fecha_rss(entry)
                    
                    # Extraer descripción
                    descripcion = entry.get('summary', '') or entry.get('description', '')
                    
                    if titulo and link:
                        noticias.append({
                            'titulo': titulo,
                            'url': link,
                            'fecha': fecha,
                            'descripcion': descripcion
                        })
                
                except Exception as e:
                    print(f"⚠️  Error procesando entrada RSS: {e}")
                    continue
            
            print(f"✅ Encontradas {len(noticias)} noticias en RSS")
            return noticias
            
        except Exception as e:
            print(f"❌ Error obteniendo RSS: {e}")
            return []
    
    def get_noticias_from_web(self, web_url: str, max_noticias: int = 20) -> List[Dict]:
        """Obtener noticias desde una página web"""
        try:
            print(f"🔍 Obteniendo noticias desde web: {web_url}")
            
            response = self.session.get(web_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar contenedor de noticias
            noticias_container = soup.find('main') or soup.find('body')
            
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
                            'url': urljoin(web_url, href),
                            'fecha': self._extract_fecha_link(link),
                            'descripcion': ''
                        })
            
            # Ordenar por fecha y limitar
            noticias_links = sorted(noticias_links, key=lambda x: x['fecha'] or datetime.now(), reverse=True)
            noticias_links = noticias_links[:max_noticias]
            
            print(f"✅ Encontradas {len(noticias_links)} noticias en web")
            return noticias_links
            
        except Exception as e:
            print(f"❌ Error obteniendo noticias web: {e}")
            return []
    
    def _extract_fecha_rss(self, entry) -> datetime:
        """Extraer fecha de una entrada RSS"""
        try:
            # Intentar diferentes campos de fecha
            fecha_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
            
            for field in fecha_fields:
                if hasattr(entry, field) and getattr(entry, field):
                    fecha_tuple = getattr(entry, field)
                    return datetime(*fecha_tuple[:6], tzinfo=timezone.utc)
            
            # Si no se encuentra, usar fecha actual
            return datetime.now(timezone.utc)
            
        except Exception as e:
            print(f"⚠️  Error extrayendo fecha RSS: {e}")
            return datetime.now(timezone.utc)
    
    def _is_noticia_link(self, href: str) -> bool:
        """Verificar si un enlace es de noticia"""
        try:
            # Patrones de URLs de noticias
            patrones = [
                r'/noticias/',
                r'/prensa/',
                r'/comunicados/',
                r'/news/',
                r'/blog/',
                r'/category/'
            ]
            
            # Patrones a excluir (navegación, paginación, etc.)
            exclusiones = [
                r'/page/',
                r'/tag/',
                r'/author/',
                r'/search',
                r'/siguiente',
                r'/anterior',
                r'/regiones',
                r'/category/regiones',
                r'/category/seminarios',
                r'/category/noticias-subsecretario',
                r'/category/noticias$'  # Solo excluir la página principal de categoría
            ]
            
            # Verificar exclusiones primero
            for exclusion in exclusiones:
                if re.search(exclusion, href, re.IGNORECASE):
                    return False
            
            # Verificar patrones de noticias
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
            return self._parse_fecha_text(fecha_texto)
        except Exception:
            return None
    
    def get_noticia_completa(self, url: str, titulo: str = None, descripcion: str = None) -> Optional[NoticiaCompleta]:
        """Obtener noticia completa desde una URL"""
        try:
            print(f"📄 Extrayendo noticia: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer información específica
            noticia = self._extract_noticia_from_page(soup, url, titulo, descripcion)
            
            if noticia:
                print(f"✅ Noticia extraída: {noticia.titulo[:50]}...")
            
            return noticia
            
        except Exception as e:
            print(f"❌ Error extrayendo noticia: {e}")
            return None
    
    def _extract_noticia_from_page(self, soup: BeautifulSoup, url: str, titulo: str = None, descripcion: str = None) -> Optional[NoticiaCompleta]:
        """Extraer noticia desde una página web"""
        try:
            # Extraer título
            titulo_elem = soup.find('h1') or soup.find('h2') or soup.find('title')
            titulo_final = titulo or (titulo_elem.get_text(strip=True) if titulo_elem else "Noticia")
            
            # Extraer fecha
            fecha = self._extract_fecha_from_page(soup)
            
            # Extraer contenido
            contenido = self._extract_contenido_from_page(soup, descripcion)
            
            if not contenido:
                return None
            
            # Crear objeto NoticiaCompleta (será sobrescrito por clases hijas)
            noticia = NoticiaCompleta(
                titulo=titulo_final,
                titulo_original=titulo_final,
                cuerpo_completo=contenido,
                fecha_publicacion=fecha,
                fuente='rss',
                fuente_nombre_completo='Fuente RSS',
                url_origen=url,
                categoria='general',
                tipo_documento='noticia'
            )
            
            return noticia
            
        except Exception as e:
            print(f"❌ Error extrayendo noticia: {e}")
            return None
    
    def _extract_fecha_from_page(self, soup: BeautifulSoup) -> datetime:
        """Extraer fecha de una página web"""
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
                    fecha_parsed = self._parse_fecha_text(fecha_texto)
                    if fecha_parsed:
                        return fecha_parsed
            
            # Si no se encuentra, usar fecha actual
            return datetime.now(timezone.utc)
            
        except Exception as e:
            print(f"⚠️  Error extrayendo fecha: {e}")
            return datetime.now(timezone.utc)
    
    def _parse_fecha_text(self, fecha_texto: str) -> Optional[datetime]:
        """Parsear fecha desde texto"""
        try:
            # Patrones de fecha comunes
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
    
    def _extract_contenido_from_page(self, soup: BeautifulSoup, descripcion: str = None) -> str:
        """Extraer contenido de una página web"""
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
            
            # Si no se encuentra, usar descripción del RSS
            if descripcion:
                return descripcion
            
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
            return descripcion or ""
    
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

class MinisterioJusticiaScraper(RSSScraper):
    """Scraper para el Ministerio de Justicia"""
    
    def __init__(self, openai_api_key: str = None):
        super().__init__(openai_api_key)
        self.rss_url = "https://www.minjusticia.gob.cl/feed/"
        self.fuente = 'ministerio_justicia'
        self.fuente_nombre = 'Ministerio de Justicia'
        # Usar la página de noticias en lugar de RSS
        self.noticias_url = "https://www.minjusticia.gob.cl/category/noticias/"
    
    def scrape_noticias_recientes(self, max_noticias: int = 10) -> List[NoticiaCompleta]:
        """Scraper completo de noticias recientes"""
        try:
            print(f"🚀 Iniciando scraping del Ministerio de Justicia...")
            
            # Intentar RSS primero
            noticias_rss = self.get_noticias_from_rss(self.rss_url, max_noticias)
            
            # Si no hay RSS, usar página web
            if not noticias_rss:
                print("📄 RSS no disponible, usando página web...")
                noticias_rss = self.get_noticias_from_web(self.noticias_url, max_noticias)
            
            if not noticias_rss:
                print("❌ No se encontraron noticias")
                return []
            
            # Extraer noticias completas
            noticias_completas = []
            
            for i, noticia_rss in enumerate(noticias_rss, 1):
                print(f"📄 Procesando noticia {i}/{len(noticias_rss)}: {noticia_rss['titulo'][:50]}...")
                
                noticia_completa = self.get_noticia_completa(
                    noticia_rss['url'],
                    noticia_rss['titulo'],
                    noticia_rss.get('descripcion', '')
                )
                
                if noticia_completa:
                    # Actualizar información específica del Ministerio
                    noticia_completa.fuente = self.fuente
                    noticia_completa.fuente_nombre_completo = self.fuente_nombre
                    noticia_completa.categoria = 'ministerio'
                    noticia_completa.jurisdiccion = 'nacional'
                    
                    noticias_completas.append(noticia_completa)
                
                # Pausa entre requests
                time.sleep(1)
            
            print(f"✅ Scraping completado: {len(noticias_completas)} noticias extraídas")
            return noticias_completas
            
        except Exception as e:
            print(f"❌ Error en scraping: {e}")
            return []

class FiscaliaScraper(RSSScraper):
    """Scraper para la Fiscalía"""
    
    def __init__(self, openai_api_key: str = None):
        super().__init__(openai_api_key)
        self.rss_url = "https://www.fiscaliadechile.cl/feed/"
        self.fuente = 'fiscalia'
        self.fuente_nombre = 'Fiscalía de Chile'
        # Usar página web como respaldo
        self.noticias_url = "https://www.fiscaliadechile.cl/noticias/"
    
    def scrape_noticias_recientes(self, max_noticias: int = 10) -> List[NoticiaCompleta]:
        """Scraper completo de noticias recientes"""
        try:
            print(f"🚀 Iniciando scraping de la Fiscalía...")
            
            # Intentar RSS primero
            noticias_rss = self.get_noticias_from_rss(self.rss_url, max_noticias)
            
            # Si no hay RSS, usar página web
            if not noticias_rss:
                print("📄 RSS no disponible, usando página web...")
                noticias_rss = self.get_noticias_from_web(self.noticias_url, max_noticias)
            
            if not noticias_rss:
                print("❌ No se encontraron noticias")
                return []
            
            # Extraer noticias completas
            noticias_completas = []
            
            for i, noticia_rss in enumerate(noticias_rss, 1):
                print(f"📄 Procesando noticia {i}/{len(noticias_rss)}: {noticia_rss['titulo'][:50]}...")
                
                noticia_completa = self.get_noticia_completa(
                    noticia_rss['url'],
                    noticia_rss['titulo'],
                    noticia_rss.get('descripcion', '')
                )
                
                if noticia_completa:
                    # Actualizar información específica de la Fiscalía
                    noticia_completa.fuente = self.fuente
                    noticia_completa.fuente_nombre_completo = self.fuente_nombre
                    noticia_completa.categoria = 'fiscalia'
                    noticia_completa.jurisdiccion = 'penal'
                    
                    noticias_completas.append(noticia_completa)
                
                # Pausa entre requests
                time.sleep(1)
            
            print(f"✅ Scraping completado: {len(noticias_completas)} noticias extraídas")
            return noticias_completas
            
        except Exception as e:
            print(f"❌ Error en scraping: {e}")
            return []

class ContraloriaScraper(RSSScraper):
    """Scraper para la Contraloría"""
    
    def __init__(self, openai_api_key: str = None):
        super().__init__(openai_api_key)
        self.rss_url = "https://www.contraloria.cl/feed/"
        self.fuente = 'contraloria'
        self.fuente_nombre = 'Contraloría General de la República'
    
    def scrape_noticias_recientes(self, max_noticias: int = 10) -> List[NoticiaCompleta]:
        """Scraper completo de noticias recientes"""
        try:
            print(f"🚀 Iniciando scraping de la Contraloría...")
            
            # Obtener noticias desde RSS
            noticias_rss = self.get_noticias_from_rss(self.rss_url, max_noticias)
            
            if not noticias_rss:
                print("❌ No se encontraron noticias")
                return []
            
            # Extraer noticias completas
            noticias_completas = []
            
            for i, noticia_rss in enumerate(noticias_rss, 1):
                print(f"📄 Procesando noticia {i}/{len(noticias_rss)}: {noticia_rss['titulo'][:50]}...")
                
                noticia_completa = self.get_noticia_completa(
                    noticia_rss['url'],
                    noticia_rss['titulo'],
                    noticia_rss['descripcion']
                )
                
                if noticia_completa:
                    # Actualizar información específica de la Contraloría
                    noticia_completa.fuente = self.fuente
                    noticia_completa.fuente_nombre_completo = self.fuente_nombre
                    noticia_completa.categoria = 'contraloria'
                    noticia_completa.jurisdiccion = 'administrativa'
                    
                    noticias_completas.append(noticia_completa)
                
                # Pausa entre requests
                time.sleep(1)
            
            print(f"✅ Scraping completado: {len(noticias_completas)} noticias extraídas")
            return noticias_completas
            
        except Exception as e:
            print(f"❌ Error en scraping: {e}")
            return []

class CDEScraper(RSSScraper):
    """Scraper para el Consejo de Defensa del Estado"""
    
    def __init__(self, openai_api_key: str = None):
        super().__init__(openai_api_key)
        self.rss_url = "https://www.cde.cl/feed/"
        self.fuente = 'cde'
        self.fuente_nombre = 'Consejo de Defensa del Estado'
    
    def scrape_noticias_recientes(self, max_noticias: int = 10) -> List[NoticiaCompleta]:
        """Scraper completo de noticias recientes"""
        try:
            print(f"🚀 Iniciando scraping del CDE...")
            
            # Obtener noticias desde RSS
            noticias_rss = self.get_noticias_from_rss(self.rss_url, max_noticias)
            
            if not noticias_rss:
                print("❌ No se encontraron noticias")
                return []
            
            # Extraer noticias completas
            noticias_completas = []
            
            for i, noticia_rss in enumerate(noticias_rss, 1):
                print(f"📄 Procesando noticia {i}/{len(noticias_rss)}: {noticia_rss['titulo'][:50]}...")
                
                noticia_completa = self.get_noticia_completa(
                    noticia_rss['url'],
                    noticia_rss['titulo'],
                    noticia_rss['descripcion']
                )
                
                if noticia_completa:
                    # Actualizar información específica del CDE
                    noticia_completa.fuente = self.fuente
                    noticia_completa.fuente_nombre_completo = self.fuente_nombre
                    noticia_completa.categoria = 'cde'
                    noticia_completa.jurisdiccion = 'civil'
                    
                    noticias_completas.append(noticia_completa)
                
                # Pausa entre requests
                time.sleep(1)
            
            print(f"✅ Scraping completado: {len(noticias_completas)} noticias extraídas")
            return noticias_completas
            
        except Exception as e:
            print(f"❌ Error en scraping: {e}")
            return []

def test_rss_scrapers():
    """Función de prueba para todos los scrapers RSS"""
    scrapers = [
        MinisterioJusticiaScraper(),
        FiscaliaScraper(),
        ContraloriaScraper(),
        CDEScraper()
    ]
    
    for scraper in scrapers:
        print(f"\n🔍 Probando {scraper.fuente_nombre}...")
        try:
            noticias = scraper.scrape_noticias_recientes(2)
            print(f"✅ {len(noticias)} noticias extraídas")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_rss_scrapers() 
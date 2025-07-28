#!/usr/bin/env python3
"""
Scraper específico para el Ministerio de Justicia de Chile
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

class MinisterioJusticiaScraper:
    """Scraper específico para el Ministerio de Justicia"""
    
    def __init__(self, openai_api_key: str = None):
        self.base_url = "https://www.minjusticia.gob.cl"
        self.noticias_url = "https://www.minjusticia.gob.cl/category/noticias/"
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
            print(f"🔍 Obteniendo noticias del Ministerio de Justicia...")
            
            response = self.session.get(self.noticias_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar enlaces de noticias específicamente
            noticias_links = []
            
            # Buscar enlaces que parezcan noticias (títulos largos, sin palabras de navegación)
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                titulo = link.get_text(strip=True)
                
                # Filtrar enlaces que parezcan noticias
                if self._es_noticia_valida(href, titulo):
                    full_url = urljoin(self.base_url, href)
                    noticias_links.append({
                        'titulo': titulo,
                        'url': full_url,
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
    
    def _es_noticia_valida(self, href: str, titulo: str) -> bool:
        """Verificar si un enlace es una noticia válida"""
        try:
            # Excluir enlaces de navegación
            exclusiones = [
                'inicio', 'ministerio', 'ministro', 'subsecretaria', 'servicios',
                'mision', 'organigrama', 'participacion', 'comunicaciones',
                'siguiente', 'anterior', 'menu', 'facebook', 'twitter', 'youtube',
                'flickr', 'outlook', 'gendarmeria', 'sml', 'sename', 'registro civil',
                'defensoria', 'caj', 'mediacion', 'transparencia', 'trabaja',
                'indicadores', 'lobby', 'solicitud', 'politicas', 'sitio historico',
                'protocolo', 'informacion', 'seguridad', 'consulta ciudadana',
                'dialogos participativos', 'participacion ciudadana'
            ]
            
            # Verificar exclusiones en el título
            titulo_lower = titulo.lower()
            for exclusion in exclusiones:
                if exclusion in titulo_lower:
                    return False
            
            # Verificar que el título sea suficientemente largo
            if len(titulo) < 20:
                return False
            
            # Verificar que la URL sea del mismo dominio
            if not href.startswith('/') and not href.startswith(self.base_url):
                return False
            
            # Verificar que no sea una página de categoría o navegación
            if any(pattern in href.lower() for pattern in ['/page/', '/category/', '/tag/', '/author/']):
                return False
            
            # Verificar que sea una noticia real (contenga palabras clave de noticias)
            palabras_clave_noticias = [
                'cuenta publica', 'inaugura', 'nombro', 'presentamos', 'mesa',
                'ley', 'estudio', 'dialogo', 'lanzamiento', 'nuevo', 'proyecto',
                'reforma', 'adopciones', 'delitos', 'intervencion', 'poblacion',
                'penal', 'interculturales', 'religiosos', 'normativa', 'penitenciaria',
                'genero', 'equidad', 'reinsercion', 'social', 'juvenil', 'abogado',
                'ninez', 'adolescencia', 'videograbadas', 'coordinacion', 'sistema',
                'justicia', 'investigaciones', 'informes', 'estudios', 'anteproyecto',
                'codigo', 'servicio', 'nacional', 'acceso', 'defensoria', 'victimas',
                'aranceles', 'receptores', 'judiciales', 'comision', 'asesora',
                'fortalecimiento', 'indh', 'auditoria', 'revision', 'especial',
                'efectuada', 'unidad', 'derechos', 'humanos', 'desnotarizacion'
            ]
            
            # Verificar que contenga al menos una palabra clave de noticias
            titulo_lower = titulo.lower()
            for palabra in palabras_clave_noticias:
                if palabra in titulo_lower:
                    return True
            
            return False
            
        except Exception:
            return False
    
    def get_noticia_completa(self, url: str, titulo: str = None) -> Optional[NoticiaCompleta]:
        """Obtener noticia completa desde una URL"""
        try:
            print(f"📄 Extrayendo noticia: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer información específica del Ministerio de Justicia
            noticia = self._extract_noticia_ministerio(soup, url, titulo)
            
            if noticia:
                print(f"✅ Noticia extraída: {noticia.titulo[:50]}...")
            
            return noticia
            
        except Exception as e:
            print(f"❌ Error extrayendo noticia: {e}")
            return None
    
    def _extract_noticia_ministerio(self, soup: BeautifulSoup, url: str, titulo: str = None) -> Optional[NoticiaCompleta]:
        """Extraer noticia específica del Ministerio de Justicia"""
        try:
            # Extraer título
            titulo_elem = soup.find('h1') or soup.find('h2') or soup.find('title')
            titulo_final = titulo or (titulo_elem.get_text(strip=True) if titulo_elem else "Noticia Ministerio de Justicia")
            
            # Extraer fecha
            fecha = self._extract_fecha_ministerio(soup)
            
            # Extraer contenido
            contenido = self._extract_contenido_ministerio(soup)
            
            if not contenido:
                return None
            
            # Crear objeto NoticiaCompleta
            noticia = NoticiaCompleta(
                titulo=titulo_final,
                titulo_original=titulo_final,
                cuerpo_completo=contenido,
                fecha_publicacion=fecha,
                fuente='ministerio_justicia',
                fuente_nombre_completo='Ministerio de Justicia y Derechos Humanos',
                url_origen=url,
                categoria='ministerio',
                tipo_documento='noticia',
                jurisdiccion='nacional'
            )
            
            return noticia
            
        except Exception as e:
            print(f"❌ Error extrayendo noticia del Ministerio: {e}")
            return None
    
    def _extract_fecha_ministerio(self, soup: BeautifulSoup) -> datetime:
        """Extraer fecha de noticia del Ministerio de Justicia"""
        try:
            # Buscar fecha en diferentes formatos
            fecha_selectors = [
                '.fecha', '.date', '.fecha-publicacion',
                'time', '[datetime]', '.meta .fecha',
                '.entry-date', '.post-date'
            ]
            
            for selector in fecha_selectors:
                fecha_elem = soup.select_one(selector)
                if fecha_elem:
                    fecha_texto = fecha_elem.get_text(strip=True)
                    fecha_parsed = self._parse_fecha_ministerio(fecha_texto)
                    if fecha_parsed:
                        return fecha_parsed
            
            # Si no se encuentra, usar fecha actual
            return datetime.now(timezone.utc)
            
        except Exception as e:
            print(f"⚠️  Error extrayendo fecha: {e}")
            return datetime.now(timezone.utc)
    
    def _parse_fecha_ministerio(self, fecha_texto: str) -> Optional[datetime]:
        """Parsear fecha del Ministerio de Justicia"""
        try:
            # Patrones de fecha comunes en el Ministerio de Justicia
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
    
    def _extract_contenido_ministerio(self, soup: BeautifulSoup) -> str:
        """Extraer contenido de noticia del Ministerio de Justicia"""
        try:
            # Buscar contenido en diferentes selectors
            contenido_selectors = [
                '.contenido', '.content', '.noticia-contenido',
                '.post-content', '.entry-content', 'article',
                '.noticia-texto', '.texto-noticia',
                '.entry', '.post'
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
    
    def _extract_fecha_link(self, link_elem) -> Optional[datetime]:
        """Extraer fecha de un enlace"""
        try:
            # Buscar fecha en el texto del enlace o elementos cercanos
            fecha_texto = link_elem.get_text(strip=True)
            return self._parse_fecha_ministerio(fecha_texto)
        except Exception:
            return None
    
    def scrape_noticias_recientes(self, max_noticias: int = 10) -> List[NoticiaCompleta]:
        """Scraper completo de noticias recientes"""
        try:
            print(f"🚀 Iniciando scraping del Ministerio de Justicia...")
            
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
    scraper = MinisterioJusticiaScraper()
    noticias = scraper.scrape_noticias_recientes(3)
    
    for noticia in noticias:
        print(f"📰 {noticia.titulo}")
        print(f"   URL: {noticia.url_origen}")
        print(f"   Fecha: {noticia.fecha_publicacion}")
        print(f"   Contenido: {len(noticia.cuerpo_completo)} caracteres")
        print("---")

if __name__ == "__main__":
    test_scraper() 
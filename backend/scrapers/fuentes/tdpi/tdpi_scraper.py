#!/usr/bin/env python3
"""
Scraper para el Tribunal de Propiedad Industrial de Chile
"""

import sys
import os
from typing import List, Dict, Optional
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import re

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from backend.scrapers.fuentes.base_scraper import BaseScraper
from backend.scrapers.fuentes.data_schema import (
    NoticiaEstandarizada, 
    DataNormalizer,
    Categoria,
    Jurisdiccion,
    TipoDocumento
)
from backend.scrapers.fuentes.date_extractor import date_extractor

class TDPScraper(BaseScraper):
    """Scraper para el Tribunal de Propiedad Industrial de Chile"""
    
    def __init__(self, openai_api_key: str = None):
        super().__init__(openai_api_key)
        self.base_url = "https://www.tdpi.cl"
        self.noticias_url = "https://www.tdpi.cl/category/noticias/"
        self.version_scraper = "1.0"
        
        # Headers específicos para TDPI
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def get_noticias_recientes(self, max_noticias: int = 20) -> List[Dict]:
        """Obtener lista de noticias recientes del TDPI"""
        try:
            self._log_info("Obteniendo noticias del Tribunal de Propiedad Industrial...")
            
            response = self.session.get(self.noticias_url, timeout=30)
            response.raise_for_status()
            
            # Configurar encoding para evitar problemas de codificación
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')  # Usar response.text en lugar de response.content
            
            # Buscar enlaces de noticias
            noticias_links = []
            
            # Método 1: Buscar títulos con enlaces "Seguir leyendo"
            # Las noticias tienen estructura: <h3>título</h3> ... <a>Seguir leyendo</a>
            h3_titles = soup.find_all('h3')
            
            for h3 in h3_titles:
                titulo = h3.get_text(strip=True)
                
                if titulo and len(titulo) > 10:
                    # Buscar el enlace "Seguir leyendo" en el siguiente contenido
                    next_sibling = h3.find_next_sibling()
                    url = None
                    
                    # Buscar en los siguientes 5 elementos hermanos
                    current = h3
                    for _ in range(5):
                        current = current.find_next()
                        if current and current.name == 'a':
                            href = current.get('href', '')
                            if href and ('seguir' in current.get_text().lower() or 
                                       '2025' in href or 'tdpi.cl' in href):
                                url = href
                                break
                        elif current and current.find('a'):
                            link = current.find('a')
                            href = link.get('href', '')
                            if href and ('seguir' in link.get_text().lower() or 
                                       '2025' in href or 'tdpi.cl' in href):
                                url = href
                                break
                    
                    # Si no se encuentra el enlace, buscar en toda la página enlaces que contengan el título
                    if not url:
                        all_links = soup.find_all('a', href=True)
                        for link in all_links:
                            href = link.get('href', '')
                            if href and ('2025' in href or 'tdpi.cl' in href):
                                # Verificar si el enlace está cerca del título
                                url = href
                                break
                    
                    if url:
                        # Construir URL completa
                        if url.startswith('/'):
                            url = self.base_url + url
                        elif not url.startswith('http'):
                            url = self.base_url + '/' + url
                        
                        noticias_links.append({
                            'url': url,
                            'titulo': titulo
                        })
                        
                        if len(noticias_links) >= max_noticias:
                            break
            
            # Método 2: Si no hay suficientes noticias, buscar enlaces que contengan fechas
            if len(noticias_links) < 3:
                # Buscar enlaces que contengan fechas (formato YYYY/MM/DD)
                date_links = soup.find_all('a', href=re.compile(r'/\d{4}/\d{2}/\d{2}/'))
                
                for link in date_links:
                    href = link.get('href', '')
                    
                    # Buscar el título en el contexto cercano
                    titulo = ""
                    
                    # Buscar título en elementos hermanos anteriores
                    prev_elem = link.find_previous(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    if prev_elem:
                        titulo = prev_elem.get_text(strip=True)
                    
                    # Si no se encuentra, extraer de la URL
                    if not titulo:
                        url_parts = href.split('/')
                        if len(url_parts) > 3:
                            last_part = url_parts[-1]
                            if last_part:
                                titulo = last_part.replace('-', ' ').replace('_', ' ').title()
                    
                    if (href and titulo and len(titulo) > 10 and
                        not any(excl in titulo.lower() for excl in ['inicio', 'menu', 'contacto', 'transparencia'])):
                        
                        # Construir URL completa
                        if href.startswith('/'):
                            url = self.base_url + href
                        elif href.startswith('http'):
                            url = href
                        else:
                            url = self.base_url + '/' + href
                        
                        # Evitar duplicados
                        if not any(n['url'] == url for n in noticias_links):
                            noticias_links.append({
                                'url': url,
                                'titulo': titulo
                            })
                            
                            if len(noticias_links) >= max_noticias:
                                break
            
            self._log_success(f"Encontradas {len(noticias_links)} noticias del TDPI")
            return noticias_links[:max_noticias]
            
        except Exception as e:
            self._log_error("Error obteniendo noticias del TDPI", e)
            return []
    
    def get_noticia_completa(self, url: str, titulo: str = None) -> Optional[NoticiaEstandarizada]:
        """Obtener noticia completa desde una URL del TDPI"""
        try:
            self._log_info(f"Extrayendo noticia del TDPI: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Configurar encoding para evitar problemas de codificación
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')  # Usar response.text en lugar de response.content
            
            # Extraer título
            if not titulo:
                titulo_elem = soup.find('h1') or soup.find('h2') or soup.find('.entry-title')
                titulo = titulo_elem.get_text(strip=True) if titulo_elem else "Sin título"
            
            # Extraer contenido - intentar múltiples selectores
            contenido = ""
            content_selectors = [
                '.entry-content',
                '.post-content',
                '.noticia-contenido',
                '.content',
                'article',
                '.main-content',
                '.noticia-body',
                '.post-body',
                '.journal-content-article',
                '.portlet-body'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Limpiar contenido
                    for script in content_elem.find_all(['script', 'style']):
                        script.decompose()
                    
                    contenido = content_elem.get_text(separator='\n', strip=True)
                    if len(contenido) > 100:  # Contenido válido
                        break
            
            # Si no se encuentra contenido, usar el título como contenido básico
            if not contenido or len(contenido) < 100:
                contenido = f"Noticia del Tribunal de Propiedad Industrial: {titulo}"
                self._log_warning(f"Contenido limitado para {url}, usando título como contenido")
            
            # Extraer fecha
            fecha = self._extract_fecha_universal(soup, url)
            if not fecha:
                fecha = datetime.now(timezone.utc)
            
            # Extraer imagen
            url_imagen = None
            img_elem = soup.find('img')
            if img_elem:
                src = img_elem.get('src', '')
                if src and not src.startswith('data:'):
                    if src.startswith('/'):
                        url_imagen = self.base_url + src
                    elif src.startswith('http'):
                        url_imagen = src
                    else:
                        url_imagen = self.base_url + '/' + src
            
            # Extraer autor
            autor = None
            autor_elem = soup.find(class_=re.compile(r'author|autor|by'))
            if autor_elem:
                autor = autor_elem.get_text(strip=True)
            
            # Clasificar noticia
            info_legal = self._extract_info_legal_tdpi(soup, contenido)
            
            # Crear noticia estandarizada
            noticia = NoticiaEstandarizada(
                titulo=titulo,
                cuerpo_completo=contenido,
                fecha_publicacion=fecha,
                fuente='tdpi',
                url_origen=url,
                **info_legal
            )
            
            if not self._validar_noticia(noticia):
                self._log_warning("Noticia del TDPI no cumple con el esquema mínimo")
                return None
            
            self._log_success(f"Noticia del TDPI extraída: {noticia.titulo[:50]}...")
            return noticia
            
        except Exception as e:
            self._log_error(f"Error extrayendo noticia del TDPI {url}", e)
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
    
    def _extract_fecha_tdpi(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extraer fecha de publicación específica de TDPI"""
        try:
            # Buscar fecha en diferentes formatos
            fecha_selectors = [
                '.fecha',
                '.date',
                '.entry-date',
                '.post-date',
                'time',
                '[datetime]',
                '.noticia-fecha',
                '.post-meta'
            ]
            
            for selector in fecha_selectors:
                fecha_elem = soup.select_one(selector)
                if fecha_elem:
                    # Intentar extraer fecha del atributo datetime
                    datetime_attr = fecha_elem.get('datetime')
                    if datetime_attr:
                        return datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                    
                    # Intentar extraer fecha del texto
                    fecha_texto = fecha_elem.get_text(strip=True)
                    if fecha_texto:
                        # Patrones de fecha comunes
                        patterns = [
                            r'(\d{1,2})/(\d{1,2})/(\d{4})',
                            r'(\d{1,2})-(\d{1,2})-(\d{4})',
                            r'(\d{4})-(\d{1,2})-(\d{1,2})'
                        ]
                        
                        for pattern in patterns:
                            match = re.search(pattern, fecha_texto)
                            if match:
                                if len(match.groups()) == 3:
                                    if len(match.group(1)) == 4:  # YYYY-MM-DD
                                        return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)), tzinfo=timezone.utc)
                                    else:  # DD/MM/YYYY o DD-MM-YYYY
                                        return datetime(int(match.group(3)), int(match.group(2)), int(match.group(1)), tzinfo=timezone.utc)
            
            return None
            
        except Exception as e:
            self._log_warning(f"Error extrayendo fecha de TDPI: {e}")
            return None
    
    def _extract_info_legal_tdpi(self, soup: BeautifulSoup, contenido: str) -> Dict:
        """Extraer información legal específica de TDPI"""
        info = {}
        
        # Clasificar por contenido
        contenido_lower = contenido.lower()
        
        # Jurisdicción
        if any(palabra in contenido_lower for palabra in ['propiedad', 'industrial', 'patente', 'marca', 'registro']):
            info['jurisdiccion'] = Jurisdiccion.COMERCIAL
        else:
            info['jurisdiccion'] = Jurisdiccion.COMERCIAL  # TDPI es principalmente comercial
        
        # Tipo de documento
        if any(palabra in contenido_lower for palabra in ['patente', 'marca', 'registro']):
            info['tipo_documento'] = TipoDocumento.RESOLUCION
        elif any(palabra in contenido_lower for palabra in ['fallo', 'sentencia']):
            info['tipo_documento'] = TipoDocumento.FALLO
        else:
            info['tipo_documento'] = TipoDocumento.COMUNICADO
        
        # Categoría
        if any(palabra in contenido_lower for palabra in ['patente', 'marca', 'registro', 'propiedad']):
            info['categoria'] = Categoria.FALLOS
        elif any(palabra in contenido_lower for palabra in ['comunicado', 'anuncio', 'información']):
            info['categoria'] = Categoria.COMUNICADOS
        else:
            info['categoria'] = Categoria.ACTIVIDADES
        
        return info
    
    def scrape_noticias_recientes(self, max_noticias: int = 10) -> List[NoticiaEstandarizada]:
        """Scrapear noticias recientes completas del TDPI"""
        self._log_info("Iniciando scraping del Tribunal de Propiedad Industrial...")
        
        # Obtener enlaces de noticias
        noticias_links = self.get_noticias_recientes(max_noticias)
        
        if not noticias_links:
            self._log_warning("No se encontraron enlaces de noticias del TDPI")
            return []
        
        # Extraer noticias completas
        noticias_completas = []
        
        for i, link in enumerate(noticias_links):
            try:
                self._log_info(f"Procesando noticia {i+1}/{len(noticias_links)}: {link['titulo'][:50]}...")
                
                noticia = self.get_noticia_completa(link['url'], link['titulo'])
                
                if noticia:
                    noticias_completas.append(noticia)
                
                # Pausa entre requests
                self._pausa_entre_requests(1)
                
            except Exception as e:
                self._log_error(f"Error procesando noticia {link['url']}", e)
                continue
        
        self._log_success(f"Scraping del TDPI completado: {len(noticias_completas)} noticias extraídas")
        return noticias_completas 
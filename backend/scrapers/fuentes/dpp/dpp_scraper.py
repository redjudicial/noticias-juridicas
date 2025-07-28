#!/usr/bin/env python3
"""
Scraper para la Defensoría Penal Pública de Chile
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

class DPPScraper(BaseScraper):
    """Scraper para la Defensoría Penal Pública de Chile"""
    
    def __init__(self, openai_api_key: str = None):
        super().__init__(openai_api_key)
        self.base_url = "https://www.dpp.cl"
        self.noticias_url = "https://www.dpp.cl/sala_prensa/noticias"
        self.version_scraper = "1.0"
        
        # Headers específicos para DPP
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def get_noticias_recientes(self, max_noticias: int = 20) -> List[Dict]:
        """Obtener lista de noticias recientes de la DPP"""
        try:
            self._log_info("Obteniendo noticias de la Defensoría Penal Pública...")
            
            response = self.session.get(self.noticias_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar enlaces de noticias
            noticias_links = []
            
            # Patrones comunes para enlaces de noticias en DPP
            selectors = [
                'a[href*="/noticias/"]',
                'a[href*="/sala_prensa/"]',
                '.noticia a',
                '.news-item a',
                '.entry-title a',
                'h2 a',
                'h3 a'
            ]
            
            for selector in selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href', '')
                    titulo = link.get_text(strip=True)
                    
                    # Filtrar enlaces válidos
                    if (href and 
                        titulo and 
                        len(titulo) > 10 and
                        not any(excl in href.lower() for excl in ['#', 'javascript:', 'mailto:']) and
                        not any(excl in titulo.lower() for excl in ['inicio', 'menu', 'contacto', 'transparencia'])):
                        
                        # Construir URL completa si es relativa
                        if href.startswith('/'):
                            url = self.base_url + href
                        elif href.startswith('http'):
                            url = href
                        else:
                            url = self.base_url + '/' + href
                        
                        noticias_links.append({
                            'url': url,
                            'titulo': titulo
                        })
                        
                        if len(noticias_links) >= max_noticias:
                            break
                
                if len(noticias_links) >= max_noticias:
                    break
            
            # Eliminar duplicados
            seen_urls = set()
            unique_links = []
            for link in noticias_links:
                if link['url'] not in seen_urls:
                    seen_urls.add(link['url'])
                    unique_links.append(link)
            
            self._log_success(f"Encontradas {len(unique_links)} noticias de la DPP")
            return unique_links[:max_noticias]
            
        except Exception as e:
            self._log_error("Error obteniendo noticias de la DPP", e)
            return []
    
    def get_noticia_completa(self, url: str, titulo: str = None) -> Optional[NoticiaEstandarizada]:
        """Obtener noticia completa desde una URL de la DPP"""
        try:
            self._log_info(f"Extrayendo noticia de la DPP: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer título
            if not titulo:
                titulo_elem = soup.find('h1') or soup.find('h2') or soup.find('.entry-title')
                titulo = titulo_elem.get_text(strip=True) if titulo_elem else "Sin título"
            
            # Extraer contenido
            contenido_selectors = [
                '.entry-content',
                '.post-content',
                '.noticia-contenido',
                '.content',
                'article',
                '.main-content'
            ]
            
            contenido = ""
            for selector in contenido_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Limpiar contenido
                    for script in content_elem.find_all(['script', 'style']):
                        script.decompose()
                    
                    contenido = content_elem.get_text(separator='\n', strip=True)
                    if len(contenido) > 100:  # Contenido válido
                        break
            
            if not contenido:
                self._log_warning(f"No se pudo extraer contenido de {url}")
                return None
            
            # Extraer fecha
            fecha = self._extract_fecha_dpp(soup)
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
            info_legal = self._extract_info_legal_dpp(soup, contenido)
            
            # Crear noticia estandarizada
            noticia = self._crear_noticia_estandarizada(
                titulo=titulo,
                cuerpo_completo=contenido,
                fecha_publicacion=fecha,
                fuente='dpp',
                fuente_nombre_completo='Defensoría Penal Pública de Chile',
                url_origen=url,
                url_imagen=url_imagen,
                autor=autor,
                version_scraper=self.version_scraper,
                **info_legal
            )
            
            if not self._validar_noticia(noticia):
                self._log_warning("Noticia de la DPP no cumple con el esquema mínimo")
                return None
            
            self._log_success(f"Noticia de la DPP extraída: {noticia.titulo[:50]}...")
            return noticia
            
        except Exception as e:
            self._log_error(f"Error extrayendo noticia de la DPP {url}", e)
            return None
    
    def _extract_fecha_dpp(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extraer fecha de publicación específica de DPP"""
        try:
            # Buscar fecha en diferentes formatos
            fecha_selectors = [
                '.fecha',
                '.date',
                '.entry-date',
                '.post-date',
                'time',
                '[datetime]'
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
            self._log_warning(f"Error extrayendo fecha de DPP: {e}")
            return None
    
    def _extract_info_legal_dpp(self, soup: BeautifulSoup, contenido: str) -> Dict:
        """Extraer información legal específica de DPP"""
        info = {}
        
        # Clasificar por contenido
        contenido_lower = contenido.lower()
        
        # Jurisdicción
        if any(palabra in contenido_lower for palabra in ['penal', 'delito', 'acusado', 'imputado', 'fiscal']):
            info['jurisdiccion'] = Jurisdiccion.PENAL
        else:
            info['jurisdiccion'] = Jurisdiccion.PENAL  # DPP es principalmente penal
        
        # Tipo de documento
        if any(palabra in contenido_lower for palabra in ['defensa', 'defensor', 'acusado']):
            info['tipo_documento'] = TipoDocumento.COMUNICADO  # Usar COMUNICADO para defensas
        else:
            info['tipo_documento'] = TipoDocumento.COMUNICADO
        
        # Categoría
        if any(palabra in contenido_lower for palabra in ['defensa', 'defensor', 'acusado', 'imputado']):
            info['categoria'] = Categoria.ACTIVIDADES  # Usar ACTIVIDADES para defensas
        elif any(palabra in contenido_lower for palabra in ['comunicado', 'anuncio', 'información']):
            info['categoria'] = Categoria.COMUNICADOS
        else:
            info['categoria'] = Categoria.ACTIVIDADES
        
        return info
    
    def scrape_noticias_recientes(self, max_noticias: int = 10) -> List[NoticiaEstandarizada]:
        """Scrapear noticias recientes completas de la DPP"""
        self._log_info("Iniciando scraping de la Defensoría Penal Pública...")
        
        # Obtener enlaces de noticias
        noticias_links = self.get_noticias_recientes(max_noticias)
        
        if not noticias_links:
            self._log_warning("No se encontraron enlaces de noticias de la DPP")
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
        
        self._log_success(f"Scraping de la DPP completado: {len(noticias_completas)} noticias extraídas")
        return noticias_completas 
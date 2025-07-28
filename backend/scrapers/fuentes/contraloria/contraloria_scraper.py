#!/usr/bin/env python3
"""
Scraper para la Contraloría General de la República de Chile
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
    MetadataNoticia,
    DataNormalizer,
    Categoria,
    Jurisdiccion,
    TipoDocumento
)

class ContraloriaScraper(BaseScraper):
    """Scraper para la Contraloría General de la República de Chile"""
    
    def __init__(self, openai_api_key: str = None):
        super().__init__(openai_api_key)
        self.base_url = "https://www.contraloria.cl"
        self.noticias_url = "https://www.contraloria.cl/portalweb/web/cgr/noticias"
        self.version_scraper = "1.0"
        
        # Headers específicos para Contraloría
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def get_noticias_recientes(self, max_noticias: int = 20) -> List[Dict]:
        """Obtener lista de noticias recientes de la Contraloría"""
        try:
            self._log_info("Obteniendo noticias de la Contraloría General de la República...")
            
            response = self.session.get(self.noticias_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer noticias con fechas de la página principal
            noticias = self._extract_noticias_con_fechas(soup, max_noticias)
            
            if noticias:
                self._log_success(f"Encontradas {len(noticias)} noticias de la Contraloría con fechas")
                return noticias
            
            # Fallback: método anterior si no se encuentran fechas
            self._log_warning("No se encontraron fechas, usando método fallback")
            return self._get_noticias_fallback(soup, max_noticias)
            
        except Exception as e:
            self._log_error("Error obteniendo noticias de la Contraloría", e)
            return []
    
    def _extract_noticias_con_fechas(self, soup: BeautifulSoup, max_noticias: int) -> List[Dict]:
        """Extraer noticias con fechas de la página principal"""
        noticias = []
        
        # Buscar patrones de fecha en el texto completo
        texto_completo = soup.get_text()
        
        # Buscar fechas en formato DD/MM/YYYY
        fechas_encontradas = re.findall(r'(\d{1,2})/(\d{1,2})/(\d{4})', texto_completo)
        
        # Buscar títulos cerca de las fechas
        for fecha_match in fechas_encontradas:
            fecha_texto = f"{fecha_match[0]}/{fecha_match[1]}/{fecha_match[2]}"
            
            # Buscar el título más cercano a esta fecha
            titulo = self._buscar_titulo_cerca_fecha(soup, fecha_texto)
            
            if titulo:
                # Buscar URL asociada al título
                url = self._buscar_url_titulo(soup, titulo)
                
                if url:
                    noticias.append({
                        'titulo': titulo,
                        'url': url,
                        'fecha': fecha_texto
                    })
                    
                    if len(noticias) >= max_noticias:
                        break
        
        return noticias
    
    def _buscar_titulo_cerca_fecha(self, soup: BeautifulSoup, fecha_texto: str) -> Optional[str]:
        """Buscar título cerca de una fecha específica"""
        # Buscar elementos que contengan la fecha
        elementos_con_fecha = soup.find_all(text=re.compile(re.escape(fecha_texto)))
        
        for elemento in elementos_con_fecha:
            # Buscar título en elementos cercanos
            parent = elemento.parent
            for _ in range(5):  # Buscar hasta 5 niveles arriba
                if parent:
                    # Buscar título en el mismo elemento o cercano
                    titulo_elem = parent.find(['h1', 'h2', 'h3', 'h4', 'a'])
                    if titulo_elem:
                        titulo = titulo_elem.get_text(strip=True)
                        if titulo and len(titulo) > 20:
                            return titulo
                    
                    # Buscar en elementos hermanos
                    for sibling in parent.find_previous_siblings():
                        titulo_elem = sibling.find(['h1', 'h2', 'h3', 'h4', 'a'])
                        if titulo_elem:
                            titulo = titulo_elem.get_text(strip=True)
                            if titulo and len(titulo) > 20:
                                return titulo
                    
                    parent = parent.parent
        
        return None
    
    def _buscar_url_titulo(self, soup: BeautifulSoup, titulo: str) -> Optional[str]:
        """Buscar URL asociada a un título"""
        # Buscar enlaces que contengan el título
        links = soup.find_all('a', href=True)
        
        for link in links:
            link_text = link.get_text(strip=True)
            if link_text == titulo or titulo in link_text:
                href = link.get('href', '')
                if href:
                    if href.startswith('/'):
                        return self.base_url + href
                    elif href.startswith('http'):
                        return href
                    else:
                        return self.base_url + '/' + href
        
        return None
    
    def _get_noticias_fallback(self, soup: BeautifulSoup, max_noticias: int) -> List[Dict]:
        """Método fallback para obtener noticias sin fechas"""
        noticias_links = []
        
        # Buscar todos los enlaces que contengan noticias
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            titulo = link.get_text(strip=True)
            
            # Filtrar enlaces válidos de noticias
            if (href and 
                titulo and 
                len(titulo) > 10 and
                ('noticias' in href.lower() or 'content' in href.lower()) and
                not any(excl in titulo.lower() for excl in ['inicio', 'menu', 'contacto', 'transparencia', 'página', 'anterior', 'siguiente'])):
                
                # Construir URL completa
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
        
        # Eliminar duplicados
        seen_urls = set()
        unique_links = []
        for link in noticias_links:
            if link['url'] not in seen_urls:
                seen_urls.add(link['url'])
                unique_links.append(link)
        
        return unique_links[:max_noticias]
    
    def get_noticia_completa(self, url: str, titulo: str = None, fecha_str: str = None) -> Optional[NoticiaEstandarizada]:
        """Obtener noticia completa desde una URL de la Contraloría"""
        try:
            self._log_info(f"Extrayendo noticia de la Contraloría: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer título
            if not titulo:
                titulo_elem = soup.find('h1') or soup.find('h2') or soup.find('.entry-title')
                titulo = titulo_elem.get_text(strip=True) if titulo_elem else "Sin título"
            
            # Extraer contenido - intentar múltiples selectores
            contenido = ""
            content_selectors = [
                '.journal-content-article',
                '.portlet-body',
                '.asset-content',
                '.entry-content',
                '.post-content',
                '.noticia-contenido',
                '.content',
                'article',
                '.main-content',
                '.noticia-body'
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
                contenido = f"Noticia de la Contraloría General de la República: {titulo}"
                self._log_warning(f"Contenido limitado para {url}, usando título como contenido")
            
            # Extraer fecha - usar la fecha de la página principal si está disponible
            if fecha_str:
                fecha = self._parse_fecha_contraloria(fecha_str)
            else:
                fecha = self._extract_fecha_contraloria(soup)
            
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
            info_legal = self._extract_info_legal_contraloria(soup, contenido)
            
            # Crear noticia estandarizada
            noticia = NoticiaEstandarizada(
                titulo=titulo[:200],
                cuerpo_completo=contenido[:2000],
                url_origen=url,
                fecha_publicacion=fecha,
                fuente="contraloria",
                categoria=info_legal.get('categoria', Categoria.ADMINISTRATIVO),
                jurisdiccion=info_legal.get('jurisdiccion', Jurisdiccion.ADMINISTRATIVO),
                tipo_documento=info_legal.get('tipo_documento', TipoDocumento.COMUNICADO),
                palabras_clave=self.extraer_palabras_clave(titulo + ' ' + contenido),
                url_imagen=url_imagen,
                metadata=MetadataNoticia(
                    autor_nombre=autor,
                    scraper_version=self.version_scraper,
                    fecha_extraccion=datetime.now(timezone.utc)
                )
            )
            
            if not self._validar_noticia(noticia):
                self._log_warning("Noticia de la Contraloría no cumple con el esquema mínimo")
                return None
            
            self._log_success(f"Noticia de la Contraloría extraída: {noticia.titulo[:50]}...")
            return noticia
            
        except Exception as e:
            self._log_error(f"Error extrayendo noticia de la Contraloría {url}", e)
            return None
    
    def _extract_fecha_contraloria(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extraer fecha de publicación específica de Contraloría"""
        try:
            # Buscar fecha en diferentes formatos
            fecha_selectors = [
                '.fecha',
                '.date',
                '.entry-date',
                '.post-date',
                'time',
                '[datetime]',
                '.noticia-fecha'
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
            self._log_warning(f"Error extrayendo fecha de Contraloría: {e}")
            return None
    
    def _parse_fecha_contraloria(self, fecha_str: str) -> Optional[datetime]:
        """Parsear fecha de la Contraloría desde string"""
        try:
            if not fecha_str:
                return None
            
            # Formato DD/MM/YYYY (como 25/07/2025)
            if re.match(r'\d{1,2}/\d{1,2}/\d{4}', fecha_str):
                return datetime.strptime(fecha_str, '%d/%m/%Y').replace(tzinfo=timezone.utc)
            
            # Formato DD-MM-YYYY
            if re.match(r'\d{1,2}-\d{1,2}-\d{4}', fecha_str):
                return datetime.strptime(fecha_str, '%d-%m-%Y').replace(tzinfo=timezone.utc)
            
            # Formato YYYY-MM-DD
            if re.match(r'\d{4}-\d{1,2}-\d{1,2}', fecha_str):
                return datetime.strptime(fecha_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            
            return None
            
        except Exception as e:
            self._log_warning(f"Error parseando fecha '{fecha_str}': {e}")
            return None
    
    def _extract_info_legal_contraloria(self, soup: BeautifulSoup, contenido: str) -> Dict:
        """Extraer información legal específica de Contraloría"""
        info = {}
        
        # Clasificar por contenido
        contenido_lower = contenido.lower()
        
        # Jurisdicción
        if any(palabra in contenido_lower for palabra in ['auditoría', 'control', 'fiscalización', 'contraloría']):
            info['jurisdiccion'] = Jurisdiccion.ADMINISTRATIVO
        else:
            info['jurisdiccion'] = Jurisdiccion.ADMINISTRATIVO  # Contraloría es principalmente administrativo
        
        # Tipo de documento
        if any(palabra in contenido_lower for palabra in ['auditoría', 'control', 'fiscalización']):
            info['tipo_documento'] = TipoDocumento.RESOLUCION
        elif any(palabra in contenido_lower for palabra in ['dictamen', 'pronunciamiento']):
            info['tipo_documento'] = TipoDocumento.DICTAMEN
        else:
            info['tipo_documento'] = TipoDocumento.COMUNICADO
        
        # Categoría
        if any(palabra in contenido_lower for palabra in ['auditoría', 'control', 'fiscalización']):
            info['categoria'] = Categoria.ADMINISTRATIVO
        elif any(palabra in contenido_lower for palabra in ['dictamen', 'pronunciamiento']):
            info['categoria'] = Categoria.ADMINISTRATIVO
        else:
            info['categoria'] = Categoria.ADMINISTRATIVO
        
        return info
    
    def scrape_noticias_recientes(self, max_noticias: int = 10) -> List[NoticiaEstandarizada]:
        """Scrapear noticias recientes completas de la Contraloría"""
        self._log_info("Iniciando scraping de la Contraloría General de la República...")
        
        # Obtener enlaces de noticias
        noticias_links = self.get_noticias_recientes(max_noticias)
        
        if not noticias_links:
            self._log_warning("No se encontraron enlaces de noticias de la Contraloría")
            return []
        
        # Extraer noticias completas
        noticias_completas = []
        
        for i, link in enumerate(noticias_links):
            try:
                self._log_info(f"Procesando noticia {i+1}/{len(noticias_links)}: {link['titulo'][:50]}...")
                
                # Pasar la fecha si está disponible
                fecha_str = link.get('fecha')
                noticia = self.get_noticia_completa(link['url'], link['titulo'], fecha_str)
                
                if noticia:
                    noticias_completas.append(noticia)
                
                # Pausa entre requests
                self._pausa_entre_requests(1)
                
            except Exception as e:
                self._log_error(f"Error procesando noticia {link['url']}", e)
                continue
        
        self._log_success(f"Scraping de la Contraloría completado: {len(noticias_completas)} noticias extraídas")
        return noticias_completas 
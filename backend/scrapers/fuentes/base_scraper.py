#!/usr/bin/env python3
"""
Scraper base para noticias jurídicas
Proporciona funcionalidades comunes para todos los scrapers
"""

import os
import sys
import requests
import time
import re
from datetime import datetime, timezone
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from abc import ABC, abstractmethod

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from backend.processors.content_processor import ContentProcessor
from .data_schema import (
    NoticiaEstandarizada, 
    DataNormalizer, 
    crear_noticia_estandarizada,
    validar_noticia_estandarizada
)

class BaseScraper(ABC):
    """Clase base para todos los scrapers de noticias jurídicas"""
    
    def __init__(self, openai_api_key: str = None):
        self.content_processor = ContentProcessor(openai_api_key or "")
        
        # Configurar sesión base
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
    
    @abstractmethod
    def get_noticias_recientes(self, max_noticias: int = 20) -> List[Dict]:
        """Obtener lista de noticias recientes - debe ser implementado por cada scraper"""
        pass
    
    @abstractmethod
    def get_noticia_completa(self, url: str, titulo: str = None) -> Optional[NoticiaEstandarizada]:
        """Obtener noticia completa - debe ser implementado por cada scraper"""
        pass
    
    @abstractmethod
    def scrape_noticias_recientes(self, max_noticias: int = 10) -> List[NoticiaEstandarizada]:
        """Scrapear noticias recientes completas - debe ser implementado por cada scraper"""
        pass
    
    def _limpiar_contenido(self, elemento) -> str:
        """Limpiar contenido HTML - método común"""
        if not elemento:
            return ""
        
        # Remover elementos no deseados
        for elem in elemento.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form']):
            elem.decompose()
        
        # Obtener texto
        texto = elemento.get_text(separator=' ', strip=True)
        
        # Limpiar espacios múltiples
        texto = re.sub(r'\s+', ' ', texto)
        
        return texto.strip()
    
    def _extract_fecha_generica(self, soup: BeautifulSoup) -> datetime:
        """Extraer fecha genérica - método común"""
        # Buscar fecha en diferentes formatos
        fecha_selectors = [
            '.fecha',
            '.fecha-publicacion',
            '.meta-fecha',
            '.noticia-fecha',
            'time',
            '[datetime]',
            '.date',
            '.published'
        ]
        
        for selector in fecha_selectors:
            fecha_elem = soup.select_one(selector)
            if fecha_elem:
                # Intentar obtener fecha del atributo datetime
                datetime_attr = fecha_elem.get('datetime')
                if datetime_attr:
                    try:
                        return datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                    except:
                        pass
                
                # Intentar parsear texto
                fecha_texto = fecha_elem.get_text(strip=True)
                fecha_parseada = self._parse_fecha_generica(fecha_texto)
                if fecha_parseada:
                    return fecha_parseada
        
        # Si no se encuentra, usar fecha actual
        return datetime.now(timezone.utc)
    
    def _parse_fecha_generica(self, fecha_texto: str) -> Optional[datetime]:
        """Parsear fecha genérica - método común"""
        if not fecha_texto:
            return None
        
        # Patrones genéricos de fecha
        patrones = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # DD/MM/YYYY
            r'(\d{1,2})-(\d{1,2})-(\d{4})',  # DD-MM-YYYY
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
            r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})',  # DD de MES de YYYY
            r'(\d{1,2})\s+(\w+)\s+(\d{4})',  # DD MES YYYY
        ]
        
        for patron in patrones:
            match = re.search(patron, fecha_texto, re.IGNORECASE)
            if match:
                try:
                    if 'de' in patron or len(match.groups()) == 3:
                        if 'de' in patron:
                            # Formato "DD de MES de YYYY"
                            dia, mes_nombre, año = match.groups()
                            meses = {
                                'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
                                'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
                                'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
                            }
                            mes = meses.get(mes_nombre.lower(), 1)
                        else:
                            # Formato numérico
                            if len(match.group(1)) == 4:  # YYYY-MM-DD
                                año, mes, dia = match.groups()
                            else:  # DD/MM/YYYY o DD-MM-YYYY
                                dia, mes, año = match.groups()
                    
                    return datetime(int(año), int(mes), int(dia), tzinfo=timezone.utc)
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def _extract_contenido_generico(self, soup: BeautifulSoup) -> str:
        """Extraer contenido genérico - método común"""
        # Buscar contenedor de contenido genérico
        contenido_selectors = [
            '.contenido',
            '.noticia-contenido',
            '.noticia-texto',
            '.noticia-cuerpo',
            'article',
            '.entry-content',
            '.post-content',
            '.main-content',
            '.content-area',
            '.article-content',
            '.story-content'
        ]
        
        for selector in contenido_selectors:
            contenido_elem = soup.select_one(selector)
            if contenido_elem:
                return self._limpiar_contenido(contenido_elem)
        
        # Si no se encuentra selector específico, buscar en el body
        body = soup.find('body')
        if body:
            # Remover elementos no deseados
            for elem in body.find_all(['nav', 'header', 'footer', 'aside', 'script', 'style']):
                elem.decompose()
            
            return self._limpiar_contenido(body)
        
        return ""
    
    def _extract_imagen_generica(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Extraer imagen genérica - método común"""
        # Buscar imagen principal genérica
        img_selectors = [
            '.noticia-imagen img',
            '.imagen-principal img',
            '.featured-image img',
            'article img',
            '.contenido img',
            '.main-content img',
            '.article-image img',
            '.story-image img'
        ]
        
        for selector in img_selectors:
            img_elem = soup.select_one(selector)
            if img_elem and img_elem.get('src'):
                src = img_elem.get('src')
                if src.startswith('http'):
                    return src
                else:
                    return urljoin(base_url, src)
        
        return None
    
    def _extract_autor_generico(self, soup: BeautifulSoup) -> Dict:
        """Extraer información del autor genérica - método común"""
        autor_info = {}
        
        # Buscar autor en diferentes formatos genéricos
        autor_selectors = [
            '.autor',
            '.author',
            '.noticia-autor',
            '.meta-autor',
            '.byline',
            '.writer',
            '.reporter'
        ]
        
        for selector in autor_selectors:
            autor_elem = soup.select_one(selector)
            if autor_elem:
                texto_autor = autor_elem.get_text(strip=True)
                if texto_autor and len(texto_autor) > 2:
                    autor_info['autor'] = texto_autor
                    break
        
        return autor_info
    
    def _pausa_entre_requests(self, segundos: int = 1):
        """Pausa entre requests para no sobrecargar servidores"""
        time.sleep(segundos)
    
    def _log_error(self, mensaje: str, error: Exception = None):
        """Log de errores común"""
        if error:
            print(f"❌ {mensaje}: {error}")
        else:
            print(f"❌ {mensaje}")
    
    def _log_success(self, mensaje: str):
        """Log de éxito común"""
        print(f"✅ {mensaje}")
    
    def _log_info(self, mensaje: str):
        """Log de información común"""
        print(f"ℹ️ {mensaje}")
    
    def _log_warning(self, mensaje: str):
        """Log de advertencia común"""
        print(f"⚠️ {mensaje}")
    
    def _crear_noticia_estandarizada(
        self,
        titulo: str,
        cuerpo_completo: str,
        fecha_publicacion: datetime,
        fuente: str,
        fuente_nombre_completo: str,
        url_origen: str,
        **kwargs
    ) -> NoticiaEstandarizada:
        """Método helper para crear noticias estandarizadas"""
        return crear_noticia_estandarizada(
            titulo=titulo,
            cuerpo_completo=cuerpo_completo,
            fecha_publicacion=fecha_publicacion,
            fuente=fuente,
            fuente_nombre_completo=fuente_nombre_completo,
            url_origen=url_origen,
            **kwargs
        )
    
    def _validar_noticia(self, noticia: NoticiaEstandarizada) -> bool:
        """Validar que una noticia cumple con el esquema"""
        return validar_noticia_estandarizada(noticia)
    
    def _normalizar_datos(self, datos_raw: Dict) -> Dict:
        """Normalizar datos raw a formato estándar"""
        datos_normalizados = {}
        
        # Normalizar título
        if 'titulo' in datos_raw:
            datos_normalizados['titulo'] = DataNormalizer.normalize_titulo(datos_raw['titulo'])
        
        # Normalizar categoría
        if 'categoria' in datos_raw:
            datos_normalizados['categoria'] = DataNormalizer.normalize_categoria(datos_raw['categoria'])
        
        # Normalizar jurisdicción
        if 'jurisdiccion' in datos_raw:
            datos_normalizados['jurisdiccion'] = DataNormalizer.normalize_jurisdiccion(datos_raw['jurisdiccion'])
        
        # Normalizar tipo de documento
        if 'tipo_documento' in datos_raw:
            datos_normalizados['tipo_documento'] = DataNormalizer.normalize_tipo_documento(datos_raw['tipo_documento'])
        
        # Copiar otros campos
        for key, value in datos_raw.items():
            if key not in ['titulo', 'categoria', 'jurisdiccion', 'tipo_documento']:
                datos_normalizados[key] = value
        
        return datos_normalizados 
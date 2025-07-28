#!/usr/bin/env python3
"""
Scraper para el Servicio de Impuestos Internos (SII) de Chile
"""

import sys
import os
from typing import List, Dict, Optional
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

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

class SIIScraper(BaseScraper):
    """Scraper para el Servicio de Impuestos Internos (SII) de Chile"""
    
    def __init__(self, openai_api_key: str = None):
        super().__init__(openai_api_key)
        self.base_url = "https://www.sii.cl"
        self.noticias_url = "https://www.sii.cl/noticias/2025/index.html"
        self.version_scraper = "1.0"
        
        # Headers específicos para SII
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def get_noticias_recientes(self, max_noticias: int = 20) -> List[Dict]:
        """Obtener lista de noticias recientes del SII"""
        try:
            print("ℹ️ Iniciando scraping del Servicio de Impuestos Internos...")
            print("ℹ️ Obteniendo noticias del SII...")
            
            response = self.session.get(self.noticias_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            noticias = []
            
            # Buscar noticias en la estructura del SII
            # Típicamente estarán en elementos con clases como 'noticia', 'item', 'entry', etc.
            enlaces_noticias = soup.find_all('a', href=True)
            
            for enlace in enlaces_noticias:
                href = enlace.get('href')
                titulo_elem = enlace.find(text=True, recursive=True)
                
                if not href or not titulo_elem:
                    continue
                
                titulo = str(titulo_elem).strip()
                
                # Filtrar enlaces relevantes (que parezcan noticias)
                if (len(titulo) > 20 and 
                    not any(excl in titulo.lower() for excl in ['menú', 'inicio', 'buscar', 'rss']) and
                    any(keyword in titulo.lower() for keyword in ['impuesto', 'tributario', 'fiscal', 'iva', 'renta', 'sii', 'contribuyente'])):
                    
                    url_completa = urljoin(self.base_url, href)
                    
                    noticias.append({
                        'titulo': titulo,
                        'url': url_completa,
                        'fecha': datetime.now().strftime('%d/%m/%Y')  # Fecha por defecto, se mejorará
                    })
                    
                    if len(noticias) >= max_noticias:
                        break
            
            print(f"✅ Encontradas {len(noticias)} noticias del SII")
            return noticias
            
        except Exception as e:
            print(f"❌ Error obteniendo noticias del SII: {str(e)}")
            return []
    
    def get_noticia_completa(self, url: str, titulo: str = None, fecha_str: str = None) -> Optional[NoticiaEstandarizada]:
        """Obtener noticia completa del SII"""
        try:
            print(f"ℹ️ Extrayendo noticia del SII: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer título si no se proporcionó
            if not titulo:
                titulo_elem = soup.find('title') or soup.find('h1')
                titulo = titulo_elem.get_text(strip=True) if titulo_elem else "Sin título"
            
            # Extraer contenido principal
            contenido = self._extraer_contenido_principal(soup)
            
            if not contenido or len(contenido) < 50:
                print("❌ Contenido insuficiente")
                return None
            
            # Extraer fecha si no se proporcionó
            fecha_publicacion = self._extraer_fecha(soup, fecha_str)
            
            # Crear noticia estandarizada
            noticia = NoticiaEstandarizada(
                titulo=titulo[:200],  # Límite de título
                cuerpo_completo=contenido[:2000],  # Límite de contenido
                fecha_publicacion=fecha_publicacion,
                fuente="sii",
                url_origen=url,
                categoria=Categoria.NORMATIVA,  # SII típicamente publica normativas
                jurisdiccion=Jurisdiccion.NACIONAL,
                tipo_documento=TipoDocumento.NOTICIA,
                fuente_nombre_completo="Servicio de Impuestos Internos",
                tribunal_organismo="SII"
            )
            
            print("✅ Noticia válida")
            print(f"✅ Noticia del SII extraída: {titulo[:50]}...")
            return noticia
            
        except Exception as e:
            print(f"❌ Error extrayendo noticia del SII {url}: {str(e)}")
            return None
    
    def _extraer_contenido_principal(self, soup: BeautifulSoup) -> str:
        """Extraer el contenido principal de la página"""
        # Buscar contenido en diferentes selectores comunes
        selectores = [
            'article',
            '.content',
            '.noticia',
            '.news-content',
            '#content',
            'main',
            '.main-content'
        ]
        
        for selector in selectores:
            contenido_elem = soup.select_one(selector)
            if contenido_elem:
                contenido = self._limpiar_contenido(contenido_elem)
                if len(contenido) > 100:
                    return contenido
        
        # Fallback: buscar en el body excluyendo navegación
        body = soup.find('body')
        if body:
            # Remover elementos de navegación
            for elem in body.find_all(['nav', 'header', 'footer', 'aside', 'menu']):
                elem.decompose()
            
            contenido = self._limpiar_contenido(body)
            return contenido
        
        return ""
    
    def _extraer_fecha(self, soup: BeautifulSoup, fecha_str: str = None) -> datetime:
        """Extraer fecha de publicación"""
        if fecha_str:
            try:
                return datetime.strptime(fecha_str, '%d/%m/%Y').replace(tzinfo=timezone.utc)
            except:
                pass
        
        # Buscar fecha en meta tags
        fecha_meta = soup.find('meta', {'name': 'date'}) or soup.find('meta', {'property': 'article:published_time'})
        if fecha_meta:
            try:
                fecha_valor = fecha_meta.get('content')
                return datetime.fromisoformat(fecha_valor.replace('Z', '+00:00'))
            except:
                pass
        
        # Buscar fecha en el texto
        texto = soup.get_text()
        patron_fecha = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', texto)
        if patron_fecha:
            try:
                dia, mes, año = patron_fecha.groups()
                return datetime(int(año), int(mes), int(dia), tzinfo=timezone.utc)
            except:
                pass
        
        # Fecha por defecto
        return datetime.now(timezone.utc)
    
    def scrape_noticias_recientes(self, max_noticias: int = 10) -> List[NoticiaEstandarizada]:
        """Scraper principal que obtiene noticias completas del SII"""
        try:
            print("🔍 Extrayendo noticias del SII...")
            
            # Obtener lista de noticias
            noticias_raw = self.get_noticias_recientes(max_noticias)
            
            if not noticias_raw:
                print("⚠️ No se encontraron noticias del SII")
                return []
            
            noticias_procesadas = []
            
            for noticia_raw in noticias_raw:
                try:
                    # Procesar cada noticia
                    noticia_completa = self.get_noticia_completa(
                        url=noticia_raw['url'],
                        titulo=noticia_raw['titulo'],
                        fecha_str=noticia_raw.get('fecha')
                    )
                    
                    if noticia_completa:
                        noticias_procesadas.append(noticia_completa)
                        
                except Exception as e:
                    print(f"❌ Error procesando noticia del SII: {str(e)}")
                    continue
            
            print(f"✅ SII: {len(noticias_procesadas)} noticias estandarizadas")
            return noticias_procesadas
            
        except Exception as e:
            print(f"❌ Error en scraping del SII: {str(e)}")
            return [] 
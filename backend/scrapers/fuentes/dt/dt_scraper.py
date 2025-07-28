#!/usr/bin/env python3
"""
Scraper para la Dirección del Trabajo (DT) de Chile
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

class DTScraper(BaseScraper):
    """Scraper para la Dirección del Trabajo (DT) de Chile"""
    
    def __init__(self, openai_api_key: str = None):
        super().__init__(openai_api_key)
        self.base_url = "https://www.dt.gob.cl"
        self.noticias_url = "https://www.dt.gob.cl/portal/1627/w3-propertyvalue-191853.html"
        self.version_scraper = "1.0"
        
        # Headers específicos para DT
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def get_noticias_recientes(self, max_noticias: int = 20) -> List[Dict]:
        """Obtener lista de noticias recientes de la DT"""
        try:
            print("ℹ️ Iniciando scraping de la Dirección del Trabajo...")
            print("ℹ️ Obteniendo noticias de la DT...")
            
            response = self.session.get(self.noticias_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            noticias = []
            
            # Buscar noticias en la estructura de la DT
            selectores_noticias = [
                '.noticia',
                '.news-item',
                '.post',
                'article',
                '.content-item',
                '.comunicado',
                'a[href*="/noticia"]',
                'a[href*="/comunicado"]',
                'a[href*="/portal"]'
            ]
            
            elementos_noticias = []
            for selector in selectores_noticias:
                elementos = soup.select(selector)
                if elementos:
                    elementos_noticias.extend(elementos[:max_noticias])
                    break
            
            # Si no encuentra elementos específicos, buscar enlaces relevantes
            if not elementos_noticias:
                enlaces = soup.find_all('a', href=True)
                for enlace in enlaces:
                    href = enlace.get('href')
                    texto = enlace.get_text(strip=True)
                    
                    if (href and texto and len(texto) > 20 and
                        any(keyword in texto.lower() for keyword in [
                            'trabajo', 'laboral', 'empleador', 'trabajador',
                            'inspección', 'fiscalización', 'sindicato', 'contrato'
                        ])):
                        
                        url_completa = urljoin(self.base_url, href)
                        fecha_elem = enlace.find_parent().find(['time', '.fecha', '.date'])
                        fecha = self._extraer_fecha_texto(fecha_elem.get_text() if fecha_elem else "")
                        
                        noticias.append({
                            'titulo': texto,
                            'url': url_completa,
                            'fecha': fecha.strftime('%d/%m/%Y') if fecha else datetime.now().strftime('%d/%m/%Y')
                        })
                        
                        if len(noticias) >= max_noticias:
                            break
            else:
                # Procesar elementos encontrados
                for elemento in elementos_noticias:
                    titulo_elem = elemento.find(['h1', 'h2', 'h3', 'h4', '.title', '.titulo'])
                    enlace_elem = elemento.find('a', href=True)
                    
                    if not titulo_elem and enlace_elem:
                        titulo_elem = enlace_elem
                    
                    if titulo_elem and enlace_elem:
                        titulo = titulo_elem.get_text(strip=True)
                        href = enlace_elem.get('href')
                        url_completa = urljoin(self.base_url, href)
                        
                        fecha_elem = elemento.find(['time', '.fecha', '.date'])
                        fecha = self._extraer_fecha_texto(fecha_elem.get_text() if fecha_elem else "")
                        
                        noticias.append({
                            'titulo': titulo,
                            'url': url_completa,
                            'fecha': fecha.strftime('%d/%m/%Y') if fecha else datetime.now().strftime('%d/%m/%Y')
                        })
            
            print(f"✅ Encontradas {len(noticias)} noticias de la DT")
            return noticias
            
        except Exception as e:
            print(f"❌ Error obteniendo noticias de la DT: {str(e)}")
            return []
    
    def _extraer_fecha_texto(self, texto: str) -> Optional[datetime]:
        """Extraer fecha de un texto"""
        if not texto:
            return None
            
        # Patrones de fecha comunes
        patrones = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
            r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})'
        ]
        
        for patron in patrones:
            match = re.search(patron, texto)
            if match:
                try:
                    if 'de' in patron:  # Formato "dd de mes de yyyy"
                        dia, mes_nombre, año = match.groups()
                        meses = {
                            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
                            'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
                            'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
                        }
                        mes = meses.get(mes_nombre.lower(), 1)
                        return datetime(int(año), mes, int(dia), tzinfo=timezone.utc)
                    else:
                        grupos = match.groups()
                        if len(grupos[0]) == 4:  # yyyy-mm-dd
                            return datetime(int(grupos[0]), int(grupos[1]), int(grupos[2]), tzinfo=timezone.utc)
                        else:  # dd-mm-yyyy
                            return datetime(int(grupos[2]), int(grupos[1]), int(grupos[0]), tzinfo=timezone.utc)
                except:
                    continue
        
        return None
    
    def get_noticia_completa(self, url: str, titulo: str = None, fecha_str: str = None) -> Optional[NoticiaEstandarizada]:
        """Obtener noticia completa de la DT"""
        try:
            print(f"ℹ️ Extrayendo noticia de la DT: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer título si no se proporcionó
            if not titulo:
                titulo_elem = soup.find('h1') or soup.find('title')
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
                fuente="dt",
                url_origen=url,
                categoria=Categoria.NORMATIVA,  # DT maneja normativas laborales
                jurisdiccion=Jurisdiccion.NACIONAL,
                tipo_documento=TipoDocumento.NOTICIA,
                fuente_nombre_completo="Dirección del Trabajo",
                tribunal_organismo="DT"
            )
            
            print("✅ Noticia válida")
            print(f"✅ Noticia de la DT extraída: {titulo[:50]}...")
            return noticia
            
        except Exception as e:
            print(f"❌ Error extrayendo noticia de la DT {url}: {str(e)}")
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
            '.main-content',
            '.post-content',
            '.entry-content'
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
        
        # Buscar fecha en elementos time
        time_elem = soup.find('time')
        if time_elem:
            datetime_attr = time_elem.get('datetime')
            if datetime_attr:
                try:
                    return datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                except:
                    pass
        
        # Buscar fecha en el texto
        texto = soup.get_text()
        fecha_extraida = self._extraer_fecha_texto(texto)
        if fecha_extraida:
            return fecha_extraida
        
        # Fecha por defecto
        return datetime.now(timezone.utc)
    
    def scrape_noticias_recientes(self, max_noticias: int = 10) -> List[NoticiaEstandarizada]:
        """Scraper principal que obtiene noticias completas de la DT"""
        try:
            print("🔍 Extrayendo noticias de la DT...")
            
            # Obtener lista de noticias
            noticias_raw = self.get_noticias_recientes(max_noticias)
            
            if not noticias_raw:
                print("⚠️ No se encontraron noticias de la DT")
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
                    print(f"❌ Error procesando noticia de la DT: {str(e)}")
                    continue
            
            print(f"✅ DT: {len(noticias_procesadas)} noticias estandarizadas")
            return noticias_procesadas
            
        except Exception as e:
            print(f"❌ Error en scraping de la DT: {str(e)}")
            return [] 
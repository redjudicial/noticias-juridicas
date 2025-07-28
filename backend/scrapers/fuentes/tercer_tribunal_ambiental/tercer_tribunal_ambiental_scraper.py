#!/usr/bin/env python3
"""
Scraper para el Tercer Tribunal Ambiental de Chile
"""
import sys
import os
from typing import List, Dict, Optional
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from backend.scrapers.fuentes.base_scraper import BaseScraper
from backend.scrapers.fuentes.data_schema import (
    NoticiaEstandarizada,
    DataNormalizer,
    Categoria,
    Jurisdiccion,
    TipoDocumento
)

class TercerTribunalAmbientalScraper(BaseScraper):
    """Scraper para el Tercer Tribunal Ambiental de Chile"""
    
    def __init__(self, openai_api_key: str = None):
        super().__init__(openai_api_key)
        self.base_url = "https://3ta.cl"
        self.noticias_url = "https://3ta.cl/category/noticias/"
        self.version_scraper = "1.0"
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def get_noticias_recientes(self, max_noticias: int = 20) -> List[Dict]:
        """Extrae las noticias más recientes del Tercer Tribunal Ambiental"""
        try:
            print(f"🔍 Extrayendo noticias de 3TA...")
            response = self.session.get(self.noticias_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            noticias = []
            
            # Buscar artículos de noticias
            articulos = soup.find_all(['article', 'div'], class_=re.compile(r'post|entry|noticia|news'))
            
            if not articulos:
                # Buscar por enlaces que contengan noticias
                enlaces = soup.find_all('a', href=re.compile(r'noticias|news'))
                
                for enlace in enlaces[:max_noticias]:
                    titulo = enlace.get_text(strip=True)
                    url = enlace['href']
                    if not url.startswith('http'):
                        url = self.base_url + url
                    
                    if titulo and len(titulo) > 10:
                        noticias.append({
                            'titulo': titulo,
                            'fecha': '',
                            'url': url,
                            'contenido': ''
                        })
            else:
                for articulo in articulos[:max_noticias]:
                    # Buscar título
                    titulo_elem = articulo.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    titulo = titulo_elem.get_text(strip=True) if titulo_elem else ""
                    
                    # Buscar fecha
                    fecha_elem = articulo.find(['time', 'span', 'div'], class_=re.compile(r'fecha|date|time'))
                    fecha = fecha_elem.get_text(strip=True) if fecha_elem else ""
                    
                    # Buscar enlace
                    link_elem = articulo.find('a', href=True)
                    url = link_elem['href'] if link_elem else self.noticias_url
                    if not url.startswith('http'):
                        url = self.base_url + url
                    
                    # Buscar contenido
                    contenido_elem = articulo.find(['p', 'div'], class_=re.compile(r'contenido|content|excerpt|resumen'))
                    contenido = contenido_elem.get_text(strip=True) if contenido_elem else ""
                    
                    if titulo and len(titulo) > 10:
                        noticias.append({
                            'titulo': titulo,
                            'fecha': fecha,
                            'url': url,
                            'contenido': contenido
                        })
            
            print(f"✅ 3TA: {len(noticias)} noticias encontradas")
            return noticias
            
        except Exception as e:
            print(f"❌ Error en 3TA: {str(e)}")
            return []

    def get_noticia_completa(self, url: str) -> Dict:
        """Obtiene el contenido completo de una noticia"""
        try:
            print(f"📄 Obteniendo noticia completa: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer título
            titulo_elem = soup.find(['h1', 'h2', 'h3'], class_=re.compile(r'titulo|title|entry-title'))
            titulo = titulo_elem.get_text(strip=True) if titulo_elem else ""
            
            # Extraer fecha
            fecha_elem = soup.find(['time', 'span', 'div'], class_=re.compile(r'fecha|date|time'))
            fecha = fecha_elem.get_text(strip=True) if fecha_elem else ""
            
            # Extraer contenido completo
            contenido_elem = soup.find(['article', 'div'], class_=re.compile(r'contenido|content|entry-content'))
            if not contenido_elem:
                contenido_elem = soup.find('body')
            
            contenido = ""
            if contenido_elem:
                # Remover elementos no deseados
                for elem in contenido_elem.find_all(['script', 'style', 'nav', 'header', 'footer']):
                    elem.decompose()
                
                contenido = contenido_elem.get_text(separator=' ', strip=True)
            
            return {
                'titulo': titulo,
                'fecha': fecha,
                'url': url,
                'contenido': contenido
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo noticia completa: {str(e)}")
            return {
                'titulo': '',
                'fecha': '',
                'url': url,
                'contenido': ''
            }

    def scrape_noticias_recientes(self, max_noticias: int = 20) -> List[NoticiaEstandarizada]:
        """Scrapea las noticias más recientes y las convierte a formato estandarizado"""
        try:
            print(f"🔄 Scrapeando noticias recientes de 3TA...")
            
            # Obtener lista de noticias
            noticias_raw = self.get_noticias_recientes(max_noticias)
            noticias_estandarizadas = []
            
            for noticia_raw in noticias_raw:
                try:
                    # Obtener contenido completo si no lo tiene
                    if not noticia_raw.get('contenido'):
                        noticia_completa = self.get_noticia_completa(noticia_raw['url'])
                        noticia_raw.update(noticia_completa)
                    
                    # Procesar y estandarizar
                    noticia_estandarizada = self.procesar_noticia(noticia_raw)
                    if noticia_estandarizada:
                        noticias_estandarizadas.append(noticia_estandarizada)
                        
                except Exception as e:
                    print(f"⚠️ Error procesando noticia: {str(e)}")
                    continue
            
            print(f"✅ 3TA: {len(noticias_estandarizadas)} noticias estandarizadas")
            return noticias_estandarizadas
            
        except Exception as e:
            print(f"❌ Error en scraping de 3TA: {str(e)}")
            return []

    def extraer_contenido_completo(self, url: str) -> str:
        """Extrae el contenido completo de una noticia específica"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar contenido principal
            contenido_selectors = [
                'article .entry-content',
                '.post-content',
                '.noticia-contenido',
                '.content-area',
                'main .content',
                '.entry-content',
                'article p',
                '.post-body'
            ]
            
            for selector in contenido_selectors:
                contenido_elem = soup.select_one(selector)
                if contenido_elem:
                    texto = contenido_elem.get_text(strip=True)
                    if len(texto) > 100:
                        return texto
            
            # Fallback: buscar todos los párrafos
            parrafos = soup.find_all('p')
            contenido = ' '.join([p.get_text(strip=True) for p in parrafos if len(p.get_text(strip=True)) > 20])
            
            return contenido if contenido else "Contenido no disponible"
            
        except Exception as e:
            print(f"❌ Error extrayendo contenido de {url}: {str(e)}")
            return "Error al extraer contenido"

    def procesar_noticia(self, noticia_raw: Dict) -> Optional[NoticiaEstandarizada]:
        """Procesa una noticia raw y la convierte al formato estandarizado"""
        try:
            # Extraer contenido completo si es necesario
            contenido = noticia_raw.get('contenido', '')
            if len(contenido) < 100 and noticia_raw.get('url') != self.noticias_url:
                contenido = self.extraer_contenido_completo(noticia_raw['url'])
            
            # Normalizar fecha
            fecha_str = noticia_raw.get('fecha', '')
            fecha = self.normalizar_fecha(fecha_str)
            
            # Crear noticia estandarizada
            noticia = NoticiaEstandarizada(
                titulo=noticia_raw.get('titulo', '')[:200],
                contenido=contenido[:2000],
                url_fuente=noticia_raw.get('url', ''),
                fecha_publicacion=fecha,
                fuente="3TA",
                categoria=Categoria.TRIBUNAL,
                jurisdiccion=Jurisdiccion.NACIONAL,
                tipo_documento=TipoDocumento.NOTICIA,
                palabras_clave=self.extraer_palabras_clave(noticia_raw.get('titulo', '') + ' ' + contenido),
                resumen_juridico="",
                embedding_vector=None,
                metadata={
                    'scraper_version': self.version_scraper,
                    'fecha_extraccion': datetime.now(timezone.utc).isoformat(),
                    'url_original': noticia_raw.get('url', '')
                }
            )
            
            return noticia
            
        except Exception as e:
            print(f"❌ Error procesando noticia 3TA: {str(e)}")
            return None

    def normalizar_fecha(self, fecha_str: str) -> datetime:
        """Normaliza diferentes formatos de fecha del 3TA"""
        try:
            if not fecha_str:
                return datetime.now(timezone.utc)
            
            # Formato: DD/MM/YYYY
            if re.match(r'\d{2}/\d{2}/\d{4}', fecha_str):
                return datetime.strptime(fecha_str, '%d/%m/%Y').replace(tzinfo=timezone.utc)
            
            # Otros formatos comunes
            formatos = [
                '%Y-%m-%d',
                '%d-%m-%Y',
                '%Y/%m/%d',
                '%d/%m/%Y %H:%M',
                '%Y-%m-%d %H:%M:%S'
            ]
            
            for formato in formatos:
                try:
                    return datetime.strptime(fecha_str, formato).replace(tzinfo=timezone.utc)
                except:
                    continue
            
            # Si no se puede parsear, usar fecha actual
            return datetime.now(timezone.utc)
            
        except Exception:
            return datetime.now(timezone.utc)

    def extraer_palabras_clave(self, texto: str) -> List[str]:
        """Extrae palabras clave relevantes del texto"""
        palabras_clave = [
            '3ta', 'tercer tribunal ambiental', 'medio ambiente', 'ambiental',
            'contaminación', 'evaluación ambiental', 'daño ambiental', 'sentencia',
            'resolución', 'recurso', 'causa', 'rol'
        ]
        
        texto_lower = texto.lower()
        encontradas = [palabra for palabra in palabras_clave if palabra in texto_lower]
        
        # Agregar palabras específicas del tribunal ambiental
        if 'sentencia' in texto_lower:
            encontradas.append('sentencia')
        if 'resolución' in texto_lower:
            encontradas.append('resolución')
        if 'recurso' in texto_lower:
            encontradas.append('recurso')
        if 'causa' in texto_lower:
            encontradas.append('causa')
        
        return list(set(encontradas))[:10]  # Máximo 10 palabras clave 
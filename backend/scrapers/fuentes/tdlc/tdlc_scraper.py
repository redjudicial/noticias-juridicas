#!/usr/bin/env python3
"""
Scraper para el Tribunal de Defensa de la Libre Competencia de Chile
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

class TDLScraper(BaseScraper):
    """Scraper para el Tribunal de Defensa de la Libre Competencia de Chile"""
    
    def __init__(self, openai_api_key: str = None):
        super().__init__(openai_api_key)
        self.base_url = "https://www.tdlc.cl"
        self.noticias_url = "https://www.tdlc.cl/noticias/"
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
        """Extrae las noticias más recientes del TDLC"""
        try:
            print(f"🔍 Extrayendo noticias de TDLC...")
            response = self.session.get(self.noticias_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            noticias = []
            
            # Buscar noticias en la página principal
            # Las noticias aparecen como bloques de texto con fechas
            noticia_blocks = soup.find_all(['div', 'article'], class_=re.compile(r'noticia|news|post|entry'))
            
            if not noticia_blocks:
                # Buscar por patrones de fecha y contenido
                fecha_pattern = re.compile(r'\d{2}/\d{2}/\d{4}')
                contenido_blocks = soup.find_all(['div', 'p'], string=fecha_pattern)
                
                for block in contenido_blocks[:max_noticias]:
                    texto = block.get_text(strip=True)
                    if fecha_pattern.search(texto):
                        # Extraer fecha y título
                        fecha_match = fecha_pattern.search(texto)
                        if fecha_match:
                            fecha_str = fecha_match.group()
                            # El título suele estar después de la fecha
                            titulo = texto[len(fecha_str):].strip()
                            if len(titulo) > 20:  # Filtrar títulos muy cortos
                                noticias.append({
                                    'titulo': titulo[:200],  # Limitar longitud
                                    'fecha': fecha_str,
                                    'url': self.noticias_url,
                                    'contenido': texto[:500]  # Primeros 500 caracteres
                                })
            else:
                for block in noticia_blocks[:max_noticias]:
                    # Buscar título
                    titulo_elem = block.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    titulo = titulo_elem.get_text(strip=True) if titulo_elem else ""
                    
                    # Buscar fecha
                    fecha_elem = block.find(['time', 'span', 'div'], class_=re.compile(r'fecha|date|time'))
                    fecha = fecha_elem.get_text(strip=True) if fecha_elem else ""
                    
                    # Buscar enlace
                    link_elem = block.find('a', href=True)
                    url = link_elem['href'] if link_elem else self.noticias_url
                    if not url.startswith('http'):
                        url = self.base_url + url
                    
                    # Buscar contenido
                    contenido_elem = block.find(['p', 'div'], class_=re.compile(r'contenido|content|excerpt|resumen'))
                    contenido = contenido_elem.get_text(strip=True) if contenido_elem else ""
                    
                    if titulo and len(titulo) > 10:
                        noticias.append({
                            'titulo': titulo,
                            'fecha': fecha,
                            'url': url,
                            'contenido': contenido
                        })
            
            print(f"✅ TDLC: {len(noticias)} noticias encontradas")
            return noticias
            
        except Exception as e:
            print(f"❌ Error en TDLC: {str(e)}")
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
                fuente="TDLC",
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
            print(f"❌ Error procesando noticia TDLC: {str(e)}")
            return None

    def normalizar_fecha(self, fecha_str: str) -> datetime:
        """Normaliza diferentes formatos de fecha del TDLC"""
        try:
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
            'tdlc', 'libre competencia', 'antimonopolio', 'competencia', 'mercado',
            'fiscalía nacional económica', 'fne', 'decreto ley 211', 'sentencia',
            'resolución', 'audiencia', 'causa', 'rol', 'demanda', 'requerimiento'
        ]
        
        texto_lower = texto.lower()
        encontradas = [palabra for palabra in palabras_clave if palabra in texto_lower]
        
        # Agregar palabras específicas del TDLC
        if 'sentencia' in texto_lower:
            encontradas.append('sentencia')
        if 'resolución' in texto_lower:
            encontradas.append('resolución')
        if 'audiencia' in texto_lower:
            encontradas.append('audiencia')
        if 'causa' in texto_lower:
            encontradas.append('causa')
        
        return list(set(encontradas))[:10]  # Máximo 10 palabras clave 

    def get_noticia_completa(self, url: str, titulo: str = None) -> Optional[NoticiaEstandarizada]:
        """Obtener noticia completa desde una URL específica"""
        try:
            contenido = self.extraer_contenido_completo(url)
            if contenido and contenido != "Error al extraer contenido":
                return self._crear_noticia_estandarizada(
                    titulo=titulo or "Noticia TDLC",
                    cuerpo_completo=contenido,
                    fecha_publicacion=datetime.now(timezone.utc),
                    fuente="TDLC",
                    fuente_nombre_completo="Tribunal de Defensa de la Libre Competencia",
                    url_origen=url
                )
            return None
        except Exception as e:
            print(f"❌ Error obteniendo noticia completa TDLC: {str(e)}")
            return None

    def scrape_noticias_recientes(self, max_noticias: int = 10) -> List[NoticiaEstandarizada]:
        """Scrapear noticias recientes completas"""
        try:
            noticias_raw = self.get_noticias_recientes(max_noticias)
            noticias_procesadas = []
            
            for noticia_raw in noticias_raw:
                noticia_procesada = self.procesar_noticia(noticia_raw)
                if noticia_procesada:
                    noticias_procesadas.append(noticia_procesada)
            
            return noticias_procesadas
        except Exception as e:
            print(f"❌ Error scrapeando noticias TDLC: {str(e)}")
            return [] 
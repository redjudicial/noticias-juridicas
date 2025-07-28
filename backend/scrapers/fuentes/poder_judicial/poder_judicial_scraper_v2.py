#!/usr/bin/env python3
"""
Scraper específico para el Poder Judicial de Chile
Optimizado para la estructura real de https://www.pjud.cl/prensa-y-comunicaciones/noticias-del-poder-judicial
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

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from backend.processors.content_processor import ContentProcessor
from ..base_scraper import BaseScraper
from ..data_schema import (
    NoticiaEstandarizada, 
    DataNormalizer,
    Categoria,
    Jurisdiccion,
    TipoDocumento
)

class PoderJudicialScraperV2(BaseScraper):
    """Scraper optimizado para el Poder Judicial de Chile"""
    
    def __init__(self, openai_api_key: str = None):
        super().__init__(openai_api_key)
        self.base_url = "https://www.pjud.cl"
        self.noticias_url = "https://www.pjud.cl/prensa-y-comunicaciones/noticias-del-poder-judicial"
        self.version_scraper = "2.0"
        
        # Configurar sesión con headers específicos para el Poder Judicial
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
    
    def get_noticias_recientes(self, max_noticias: int = 20) -> List[Dict]:
        """Obtener lista de noticias recientes del Poder Judicial"""
        try:
            self._log_info("Obteniendo noticias del Poder Judicial...")
            
            response = self.session.get(self.noticias_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar noticias específicas del Poder Judicial
            noticias_links = []
            
            # Buscar enlaces que contengan noticias específicas
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                titulo = link.get_text(strip=True)
                
                # Filtrar noticias específicas del Poder Judicial
                if self._es_noticia_poder_judicial(titulo, href):
                    # Construir URL completa
                    if href.startswith('http'):
                        url_completa = href
                    else:
                        url_completa = urljoin(self.base_url, href)
                    
                    # Extraer fecha del texto del enlace
                    fecha = self._extract_fecha_from_text(titulo)
                    
                    noticias_links.append({
                        'titulo': titulo,
                        'url': url_completa,
                        'fecha': fecha
                    })
            
            # Ordenar por fecha y limitar
            noticias_links = sorted(noticias_links, key=lambda x: x['fecha'] or datetime.now(timezone.utc), reverse=True)
            noticias_links = noticias_links[:max_noticias]
            
            self._log_success(f"Encontradas {len(noticias_links)} noticias del Poder Judicial")
            return noticias_links
            
        except Exception as e:
            self._log_error("Error obteniendo noticias del Poder Judicial", e)
            return []
    
    def _es_noticia_poder_judicial(self, titulo: str, href: str) -> bool:
        """Verificar si es una noticia específica del Poder Judicial"""
        if not titulo or len(titulo) < 20:
            return False
        
        # Palabras clave específicas del Poder Judicial
        palabras_clave = [
            'fiscal', 'corte', 'juzgado', 'tribunal', 'sentencia', 'fallo', 
            'condena', 'prisión', 'acusado', 'imputado', 'sumario', 'querella',
            'liquidación', 'robo', 'abuso', 'violación', 'homicidio', 'alcalde',
            'ejército', 'garantía', 'apelaciones', 'suprema', 'oral', 'penal',
            'civil', 'familia', 'laboral', 'cobranza', 'administrativo'
        ]
        
        # Exclusiones
        exclusiones = [
            'anterior', 'siguiente', 'última', 'página', 'filtrar', 'inicio',
            'menu', 'portal', 'sistema', 'traducción', 'licitaciones'
        ]
        
        # Verificar exclusiones
        if any(exclusion in titulo.lower() for exclusion in exclusiones):
            return False
        
        # Verificar palabras clave
        if any(keyword in titulo.lower() for keyword in palabras_clave):
            return True
        
        # Verificar si la URL contiene patrones de noticias
        if '/noticias-del-poder-judicial/' in href:
            return True
        
        return False
    
    def _extract_fecha_from_text(self, texto: str) -> Optional[datetime]:
        """Extraer fecha del texto de la noticia del Poder Judicial"""
        # Patrones de fecha específicos del Poder Judicial
        patrones = [
            r'(\d{1,2})-(\d{1,2})-(\d{4})\s+(\d{1,2}):(\d{1,2})',  # DD-MM-YYYY HH:MM
            r'(\d{1,2})-(\d{1,2})-(\d{4})',  # DD-MM-YYYY
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # DD/MM/YYYY
        ]
        
        for patron in patrones:
            match = re.search(patron, texto)
            if match:
                try:
                    if len(match.groups()) == 5:  # Con hora
                        dia, mes, año, hora, minuto = match.groups()
                        return datetime(int(año), int(mes), int(dia), int(hora), int(minuto), tzinfo=timezone.utc)
                    else:  # Solo fecha
                        dia, mes, año = match.groups()
                        return datetime(int(año), int(mes), int(dia), tzinfo=timezone.utc)
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def get_noticia_completa(self, url: str, titulo: str = None) -> Optional[NoticiaEstandarizada]:
        """Obtener noticia completa desde una URL del Poder Judicial"""
        try:
            self._log_info(f"Extrayendo noticia del Poder Judicial: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer información específica del Poder Judicial
            noticia = self._extract_noticia_poder_judicial(soup, url, titulo)
            
            if noticia:
                self._log_success(f"Noticia del Poder Judicial extraída: {noticia.titulo[:50]}...")
            
            return noticia
            
        except Exception as e:
            self._log_error(f"Error extrayendo noticia del Poder Judicial {url}", e)
            return None
    
    def _extract_noticia_poder_judicial(self, soup: BeautifulSoup, url: str, titulo: str = None) -> Optional[NoticiaEstandarizada]:
        """Extraer noticia específica del Poder Judicial"""
        try:
            # Buscar título
            titulo_elem = (
                soup.find('h1', class_='titulo') or
                soup.find('h1') or
                soup.find('h2', class_='titulo') or
                soup.find('h2') or
                soup.find(class_=re.compile(r'titulo|title', re.I))
            )
            
            titulo = titulo or (titulo_elem.get_text(strip=True) if titulo_elem else "Sin título")
            
            # Buscar fecha
            fecha = self._extract_fecha_poder_judicial(soup)
            
            # Buscar contenido
            contenido = self._extract_contenido_poder_judicial(soup)
            
            # Extraer información legal específica del Poder Judicial
            info_legal = self._extract_info_legal_poder_judicial(soup, contenido)
            
            # Extraer imagen si existe
            imagen_url = self._extract_imagen_poder_judicial(soup)
            
            # Extraer autor si existe
            autor_info = self._extract_autor_poder_judicial(soup)
            
            # Crear noticia estandarizada
            noticia = self._crear_noticia_estandarizada(
                titulo=titulo,
                cuerpo_completo=contenido,
                fecha_publicacion=fecha,
                fuente='poder_judicial',
                fuente_nombre_completo='Poder Judicial de Chile',
                url_origen=url,
                url_imagen=imagen_url,
                autor=autor_info.get('autor'),
                autor_cargo=autor_info.get('cargo'),
                version_scraper=self.version_scraper,
                **info_legal
            )
            
            # Validar noticia
            if not self._validar_noticia(noticia):
                self._log_warning("Noticia del Poder Judicial no cumple con el esquema mínimo")
                return None
            
            return noticia
            
        except Exception as e:
            self._log_error("Error en extracción específica del Poder Judicial", e)
            return None
    
    def _extract_fecha_poder_judicial(self, soup: BeautifulSoup) -> datetime:
        """Extraer fecha específica del Poder Judicial"""
        # Buscar fecha en diferentes formatos del Poder Judicial
        fecha_selectors = [
            '.fecha',
            '.fecha-publicacion',
            '.meta-fecha',
            '.noticia-fecha',
            'time',
            '[datetime]'
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
                fecha_parseada = self._parse_fecha_poder_judicial(fecha_texto)
                if fecha_parseada:
                    return fecha_parseada
        
        # Si no se encuentra, usar fecha actual
        return datetime.now(timezone.utc)
    
    def _parse_fecha_poder_judicial(self, fecha_texto: str) -> Optional[datetime]:
        """Parsear fecha específica del formato del Poder Judicial"""
        if not fecha_texto:
            return None
        
        # Patrones específicos del Poder Judicial
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
    
    def _extract_contenido_poder_judicial(self, soup: BeautifulSoup) -> str:
        """Extraer contenido específico del Poder Judicial"""
        # Buscar contenedor de contenido específico del Poder Judicial
        contenido_selectors = [
            '.contenido',
            '.noticia-contenido',
            '.noticia-texto',
            '.noticia-cuerpo',
            'article',
            '.entry-content',
            '.post-content',
            '.main-content',
            '.content-area'
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
    
    def _extract_info_legal_poder_judicial(self, soup: BeautifulSoup, contenido: str) -> Dict:
        """Extraer información legal específica del Poder Judicial"""
        info = {}
        
        # Buscar número de causa específico del Poder Judicial
        causa_patterns = [
            r'causa\s+(?:rol\s+)?(\d+[-/]\d+)',
            r'rol\s+(\d+[-/]\d+)',
            r'causa\s+n[°º]\s*(\d+[-/]\d+)',
            r'(\d+[-/]\d+)\s*\(?rol\)?',
            r'causa\s+(\d+[-/]\d+)',
            r'(\d+[-/]\d+)\s*\(?causa\)?'
        ]
        
        for pattern in causa_patterns:
            match = re.search(pattern, contenido, re.IGNORECASE)
            if match:
                info['numero_causa'] = match.group(1)
                info['rol_causa'] = match.group(1)
                break
        
        # Buscar tribunal específico del Poder Judicial
        tribunales = [
            'Corte Suprema',
            'Corte de Apelaciones',
            'Juzgado Civil',
            'Juzgado Penal',
            'Juzgado de Familia',
            'Juzgado de Garantía',
            'Tribunal Oral en lo Penal',
            'Juzgado de Letras',
            'Juzgado de Cobranza',
            'Juzgado Laboral',
            'Juzgado de Policía Local'
        ]
        
        for tribunal in tribunales:
            if tribunal.lower() in contenido.lower():
                info['tribunal_organismo'] = tribunal
                break
        
        # Determinar jurisdicción específica del Poder Judicial
        if any(palabra in contenido.lower() for palabra in ['penal', 'delito', 'acusado', 'fiscal', 'defensor', 'prisión']):
            info['jurisdiccion'] = Jurisdiccion.PENAL
        elif any(palabra in contenido.lower() for palabra in ['civil', 'contrato', 'propiedad', 'familia', 'divorcio']):
            info['jurisdiccion'] = Jurisdiccion.CIVIL
        elif any(palabra in contenido.lower() for palabra in ['laboral', 'trabajo', 'empleado', 'patrón']):
            info['jurisdiccion'] = Jurisdiccion.LABORAL
        elif any(palabra in contenido.lower() for palabra in ['administrativo', 'estado', 'gobierno', 'municipal']):
            info['jurisdiccion'] = Jurisdiccion.ADMINISTRATIVO
        else:
            info['jurisdiccion'] = Jurisdiccion.GENERAL
        
        # Determinar tipo de documento específico del Poder Judicial
        if any(palabra in contenido.lower() for palabra in ['fallo', 'sentencia', 'resolucion']):
            info['tipo_documento'] = TipoDocumento.FALLO
        elif 'resolución' in contenido.lower():
            info['tipo_documento'] = TipoDocumento.RESOLUCION
        elif 'acuerdo' in contenido.lower():
            info['tipo_documento'] = TipoDocumento.ACUERDO
        elif 'comunicado' in contenido.lower():
            info['tipo_documento'] = TipoDocumento.COMUNICADO
        else:
            info['tipo_documento'] = TipoDocumento.NOTICIA
        
        # Extraer categoría específica del Poder Judicial
        if 'fallo' in contenido.lower() or 'sentencia' in contenido.lower():
            info['categoria'] = Categoria.FALLOS
        elif 'actividad' in contenido.lower() or 'evento' in contenido.lower():
            info['categoria'] = Categoria.ACTIVIDADES
        elif 'comunicado' in contenido.lower():
            info['categoria'] = Categoria.COMUNICADOS
        else:
            info['categoria'] = Categoria.NOTICIAS
        
        return info
    
    def _extract_imagen_poder_judicial(self, soup: BeautifulSoup) -> Optional[str]:
        """Extraer imagen de la noticia del Poder Judicial"""
        # Buscar imagen principal específica del Poder Judicial
        img_selectors = [
            '.noticia-imagen img',
            '.imagen-principal img',
            '.featured-image img',
            'article img',
            '.contenido img',
            '.main-content img'
        ]
        
        for selector in img_selectors:
            img_elem = soup.select_one(selector)
            if img_elem and img_elem.get('src'):
                src = img_elem.get('src')
                if src.startswith('http'):
                    return src
                else:
                    return urljoin(self.base_url, src)
        
        return None
    
    def _extract_autor_poder_judicial(self, soup: BeautifulSoup) -> Dict:
        """Extraer información del autor del Poder Judicial"""
        autor_info = {}
        
        # Buscar autor en diferentes formatos del Poder Judicial
        autor_selectors = [
            '.autor',
            '.author',
            '.noticia-autor',
            '.meta-autor',
            '.byline'
        ]
        
        for selector in autor_selectors:
            autor_elem = soup.select_one(selector)
            if autor_elem:
                texto_autor = autor_elem.get_text(strip=True)
                if texto_autor and len(texto_autor) > 2:
                    autor_info['autor'] = texto_autor
                    break
        
        return autor_info
    
    def scrape_noticias_recientes(self, max_noticias: int = 10) -> List[NoticiaEstandarizada]:
        """Scrapear noticias recientes completas del Poder Judicial"""
        self._log_info("Iniciando scraping del Poder Judicial...")
        
        # Obtener lista de noticias
        noticias_links = self.get_noticias_recientes(max_noticias)
        
        if not noticias_links:
            self._log_warning("No se encontraron noticias del Poder Judicial")
            return []
        
        # Extraer noticias completas
        noticias_completas = []
        
        for i, noticia_link in enumerate(noticias_links, 1):
            self._log_info(f"Procesando noticia {i}/{len(noticias_links)}: {noticia_link['titulo'][:50]}...")
            
            noticia_completa = self.get_noticia_completa(
                noticia_link['url'], 
                noticia_link['titulo']
            )
            
            if noticia_completa:
                noticias_completas.append(noticia_completa)
            
            # Pausa entre requests para no sobrecargar el servidor
            self._pausa_entre_requests(1)
        
        self._log_success(f"Scraping del Poder Judicial completado: {len(noticias_completas)} noticias extraídas")
        return noticias_completas

# Función de prueba específica para el Poder Judicial
def test_poder_judicial_scraper():
    """Función de prueba del scraper del Poder Judicial"""
    scraper = PoderJudicialScraperV2()
    
    print("🧪 Probando scraper del Poder Judicial (V2) con esquema estandarizado...")
    
    # Probar obtención de noticias recientes
    noticias_links = scraper.get_noticias_recientes(3)
    
    if noticias_links:
        print(f"✅ Encontradas {len(noticias_links)} noticias del Poder Judicial")
        
        # Probar extracción de una noticia
        primera_noticia = noticias_links[0]
        print(f"📄 Probando extracción: {primera_noticia['titulo']}")
        
        noticia_completa = scraper.get_noticia_completa(
            primera_noticia['url'],
            primera_noticia['titulo']
        )
        
        if noticia_completa:
            print(f"✅ Noticia del Poder Judicial extraída exitosamente:")
            print(f"   Título: {noticia_completa.titulo}")
            print(f"   Fuente: {noticia_completa.fuente}")
            print(f"   Fecha: {noticia_completa.fecha_publicacion}")
            print(f"   Contenido: {len(noticia_completa.cuerpo_completo)} caracteres")
            print(f"   Jurisdicción: {noticia_completa.jurisdiccion}")
            print(f"   Tipo: {noticia_completa.tipo_documento}")
            print(f"   Categoría: {noticia_completa.categoria}")
            print(f"   Hash: {noticia_completa.hash_contenido}")
            print(f"   Válida: {scraper._validar_noticia(noticia_completa)}")
        else:
            print("❌ Error extrayendo noticia del Poder Judicial")
    else:
        print("❌ No se encontraron noticias del Poder Judicial")

if __name__ == "__main__":
    test_poder_judicial_scraper() 
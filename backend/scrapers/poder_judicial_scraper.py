#!/usr/bin/env python3
"""
Scraper para el Poder Judicial de Chile
Extrae noticias completas de https://www.pjud.cl
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

class PoderJudicialScraper:
    """Scraper para el Poder Judicial de Chile"""
    
    def __init__(self, openai_api_key: str = None):
        self.base_url = "https://www.pjud.cl"
        self.noticias_url = "https://www.pjud.cl/prensa-y-comunicaciones/noticias-del-poder-judicial"
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
            print(f"🔍 Obteniendo noticias del Poder Judicial...")
            
            response = self.session.get(self.noticias_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar noticias en la estructura específica del Poder Judicial
            noticias_links = []
            
            # Buscar enlaces que contengan noticias específicas
            # Basado en la estructura real de la página
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                titulo = link.get_text(strip=True)
                
                # Filtrar noticias específicas del Poder Judicial
                if (titulo and len(titulo) > 20 and 
                    any(keyword in titulo.lower() for keyword in [
                        'fiscal', 'corte', 'juzgado', 'tribunal', 'sentencia', 
                        'fallo', 'condena', 'prisión', 'acusado', 'imputado',
                        'sumario', 'querella', 'liquidación', 'robo', 'abuso',
                        'violación', 'homicidio', 'alcalde', 'ejército'
                    ]) and
                    not any(exclusion in titulo.lower() for exclusion in [
                        'anterior', 'siguiente', 'última', 'página', 'filtrar'
                    ])):
                    
                    # Construir URL completa
                    if href.startswith('http'):
                        url_completa = href
                    else:
                        url_completa = urljoin(self.base_url, href)
                    
                    # Extraer fecha del texto del enlace o elementos cercanos
                    fecha = self._extract_fecha_from_text(titulo)
                    
                    noticias_links.append({
                        'titulo': titulo,
                        'url': url_completa,
                        'fecha': fecha
                    })
            
            # Ordenar por fecha y limitar
            noticias_links = sorted(noticias_links, key=lambda x: x['fecha'] or datetime.now(timezone.utc), reverse=True)
            noticias_links = noticias_links[:max_noticias]
            
            print(f"✅ Encontradas {len(noticias_links)} noticias")
            return noticias_links
            
        except Exception as e:
            print(f"❌ Error obteniendo noticias: {e}")
            return []
    
    def get_noticia_completa(self, url: str, titulo: str = None) -> Optional[NoticiaCompleta]:
        """Obtener noticia completa desde una URL"""
        try:
            print(f"📄 Extrayendo noticia: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer información específica del Poder Judicial
            noticia = self._extract_noticia_poder_judicial(soup, url, titulo)
            
            if noticia:
                print(f"✅ Noticia extraída: {noticia.titulo[:50]}...")
            
            return noticia
            
        except Exception as e:
            print(f"❌ Error extrayendo noticia {url}: {e}")
            return None
    
    def _extract_noticia_poder_judicial(self, soup: BeautifulSoup, url: str, titulo: str = None) -> Optional[NoticiaCompleta]:
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
            
            # Extraer información legal específica
            info_legal = self._extract_info_legal_poder_judicial(soup, contenido)
            
            # Extraer imagen si existe
            imagen_url = self._extract_imagen_poder_judicial(soup)
            
            # Extraer autor si existe
            autor_info = self._extract_autor_poder_judicial(soup)
            
            return NoticiaCompleta(
                titulo=titulo,
                titulo_original=titulo,
                cuerpo_completo=contenido,
                fecha_publicacion=fecha,
                fuente='poder_judicial',
                fuente_nombre_completo='Poder Judicial de Chile',
                url_origen=url,
                url_imagen=imagen_url,
                autor=autor_info.get('autor'),
                autor_cargo=autor_info.get('cargo'),
                **info_legal
            )
            
        except Exception as e:
            print(f"❌ Error en extracción específica: {e}")
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
        
        # Buscar fecha en el texto de la página
        texto_completo = soup.get_text()
        fecha_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', texto_completo)
        if fecha_match:
            dia, mes, año = fecha_match.groups()
            try:
                return datetime(int(año), int(mes), int(dia), tzinfo=timezone.utc)
            except:
                pass
        
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
    
    def _extract_contenido_poder_judicial(self, soup: BeautifulSoup) -> str:
        """Extraer contenido específico del Poder Judicial"""
        # Buscar contenedor de contenido
        contenido_selectors = [
            '.contenido',
            '.noticia-contenido',
            '.noticia-texto',
            '.noticia-cuerpo',
            'article',
            '.entry-content',
            '.post-content'
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
    
    def _limpiar_contenido(self, elemento) -> str:
        """Limpiar contenido HTML"""
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
    
    def _extract_info_legal_poder_judicial(self, soup: BeautifulSoup, contenido: str) -> Dict:
        """Extraer información legal específica del Poder Judicial"""
        info = {}
        
        # Buscar número de causa
        causa_patterns = [
            r'causa\s+(?:rol\s+)?(\d+[-/]\d+)',
            r'rol\s+(\d+[-/]\d+)',
            r'causa\s+n[°º]\s*(\d+[-/]\d+)',
            r'(\d+[-/]\d+)\s*\(?rol\)?'
        ]
        
        for pattern in causa_patterns:
            match = re.search(pattern, contenido, re.IGNORECASE)
            if match:
                info['numero_causa'] = match.group(1)
                info['rol_causa'] = match.group(1)
                break
        
        # Buscar tribunal
        tribunales = [
            'Corte Suprema',
            'Corte de Apelaciones',
            'Juzgado Civil',
            'Juzgado Penal',
            'Juzgado de Familia',
            'Juzgado de Garantía',
            'Tribunal Oral en lo Penal',
            'Juzgado de Letras'
        ]
        
        for tribunal in tribunales:
            if tribunal.lower() in contenido.lower():
                info['tribunal_organismo'] = tribunal
                break
        
        # Determinar jurisdicción
        if any(palabra in contenido.lower() for palabra in ['penal', 'delito', 'acusado', 'fiscal', 'defensor']):
            info['jurisdiccion'] = 'penal'
        elif any(palabra in contenido.lower() for palabra in ['civil', 'contrato', 'propiedad', 'familia']):
            info['jurisdiccion'] = 'civil'
        elif any(palabra in contenido.lower() for palabra in ['administrativo', 'estado', 'gobierno']):
            info['jurisdiccion'] = 'administrativo'
        else:
            info['jurisdiccion'] = 'general'
        
        # Determinar tipo de documento
        if any(palabra in contenido.lower() for palabra in ['fallo', 'sentencia', 'resolucion']):
            info['tipo_documento'] = 'fallo'
        elif 'resolución' in contenido.lower():
            info['tipo_documento'] = 'resolucion'
        elif 'acuerdo' in contenido.lower():
            info['tipo_documento'] = 'acuerdo'
        else:
            info['tipo_documento'] = 'comunicado'
        
        # Extraer categoría
        if 'fallo' in contenido.lower() or 'sentencia' in contenido.lower():
            info['categoria'] = 'fallos'
        elif 'actividad' in contenido.lower() or 'evento' in contenido.lower():
            info['categoria'] = 'actividades'
        else:
            info['categoria'] = 'comunicados'
        
        return info
    
    def _extract_imagen_poder_judicial(self, soup: BeautifulSoup) -> Optional[str]:
        """Extraer imagen de la noticia"""
        # Buscar imagen principal
        img_selectors = [
            '.noticia-imagen img',
            '.imagen-principal img',
            '.featured-image img',
            'article img',
            '.contenido img'
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
        """Extraer información del autor"""
        autor_info = {}
        
        # Buscar autor en diferentes formatos
        autor_selectors = [
            '.autor',
            '.author',
            '.noticia-autor',
            '.meta-autor'
        ]
        
        for selector in autor_selectors:
            autor_elem = soup.select_one(selector)
            if autor_elem:
                texto_autor = autor_elem.get_text(strip=True)
                if texto_autor and len(texto_autor) > 2:
                    autor_info['autor'] = texto_autor
                    break
        
        return autor_info
    
    def _is_noticia_link(self, href: str) -> bool:
        """Verificar si un enlace es de noticia"""
        # Patrones de URLs de noticias del Poder Judicial
        noticia_patterns = [
            r'/noticias/',
            r'/prensa/',
            r'/comunicaciones/',
            r'/noticia/',
            r'/news/'
        ]
        
        return any(re.search(pattern, href, re.IGNORECASE) for pattern in noticia_patterns)
    
    def _extract_fecha_from_text(self, texto: str) -> Optional[datetime]:
        """Extraer fecha del texto de la noticia"""
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
    
    def _extract_fecha_link(self, link_elem) -> Optional[datetime]:
        """Extraer fecha de un enlace de noticia"""
        # Buscar fecha en el elemento padre o hermanos
        parent = link_elem.parent
        if parent:
            # Buscar elementos de fecha cercanos
            fecha_elem = parent.find(class_=re.compile(r'fecha|date|time', re.I))
            if fecha_elem:
                fecha_texto = fecha_elem.get_text(strip=True)
                return self._parse_fecha_poder_judicial(fecha_texto)
        
        return None
    
    def scrape_noticias_recientes(self, max_noticias: int = 10) -> List[NoticiaCompleta]:
        """Scrapear noticias recientes completas"""
        print(f"🚀 Iniciando scraping del Poder Judicial...")
        
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

# Función de prueba
def test_scraper():
    """Función de prueba del scraper"""
    scraper = PoderJudicialScraper()
    
    print("🧪 Probando scraper del Poder Judicial...")
    
    # Probar obtención de noticias recientes
    noticias_links = scraper.get_noticias_recientes(5)
    
    if noticias_links:
        print(f"✅ Encontradas {len(noticias_links)} noticias")
        
        # Probar extracción de una noticia
        primera_noticia = noticias_links[0]
        print(f"📄 Probando extracción: {primera_noticia['titulo']}")
        
        noticia_completa = scraper.get_noticia_completa(
            primera_noticia['url'],
            primera_noticia['titulo']
        )
        
        if noticia_completa:
            print(f"✅ Noticia extraída exitosamente:")
            print(f"   Título: {noticia_completa.titulo}")
            print(f"   Fuente: {noticia_completa.fuente}")
            print(f"   Fecha: {noticia_completa.fecha_publicacion}")
            print(f"   Contenido: {len(noticia_completa.cuerpo_completo)} caracteres")
            print(f"   Jurisdicción: {noticia_completa.jurisdiccion}")
            print(f"   Tipo: {noticia_completa.tipo_documento}")
        else:
            print("❌ Error extrayendo noticia")
    else:
        print("❌ No se encontraron noticias")

if __name__ == "__main__":
    test_scraper() 
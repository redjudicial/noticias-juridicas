#!/usr/bin/env python3
"""
Extractor universal de fechas para todas las fuentes
Maneja múltiples formatos de fecha encontrados en noticias jurídicas
"""

import re
from datetime import datetime, timezone
from typing import Optional, List
from bs4 import BeautifulSoup

class UniversalDateExtractor:
    """Extractor universal de fechas para noticias jurídicas"""
    
    def __init__(self):
        self.meses = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
            'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
            'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12,
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
            'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
            'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        # Patrones de fecha universales
        self.patrones = [
            # Formato DD/MM/YYYY o DD-MM-YYYY o DD.MM.YYYY
            r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{4})',
            
            # Formato YYYY-MM-DD
            r'(\d{4})-(\d{1,2})-(\d{1,2})',
            
            # Formato DD de Mes de YYYY (español)
            r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})',
            r'(\d{1,2})\s+de\s+(\w+)\s+del\s+(\d{4})',
            
            # Formato Mes DD, YYYY (inglés)
            r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',
            
            # Formato DD Mes YYYY
            r'(\d{1,2})\s+(\w+)\s+(\d{4})',
            
            # Formato con día de la semana
            r'(\w+),\s+(\d{1,2})\s+(\w+)\s+(\d{4})',
            
            # Formato ISO
            r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})',
            
            # Formato DD/MM/YY (año corto)
            r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2})',
        ]
    
    def extract_date_from_html(self, soup: BeautifulSoup, url: str = None) -> Optional[datetime]:
        """
        Extraer fecha de una página HTML usando múltiples estrategias
        """
        # Estrategia 1: Buscar en elementos específicos de fecha
        fecha = self._extract_from_date_elements(soup)
        if fecha:
            return fecha
        
        # Estrategia 2: Buscar en el contenido completo
        fecha = self._extract_from_content(soup.get_text())
        if fecha:
            return fecha
        
        # Estrategia 3: Buscar en la URL (si contiene fecha)
        if url:
            fecha = self._extract_from_url(url)
            if fecha:
                return fecha
        
        # Estrategia 4: Buscar en meta tags
        fecha = self._extract_from_meta_tags(soup)
        if fecha:
            return fecha
        
        return None
    
    def _extract_from_date_elements(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extraer fecha de elementos específicos de fecha"""
        selectors = [
            '.fecha', '.date', '.fecha-publicacion', '.fecha-noticia',
            'time', '[datetime]', '.meta .fecha', '.entry-date', '.post-date',
            '.noticia-fecha', '.publicacion-fecha', '.fecha-articulo',
            '.fecha-creacion', '.fecha-modificacion', '.fecha-actualizacion'
        ]
        
        for selector in selectors:
            elementos = soup.select(selector)
            for elemento in elementos:
                # Buscar en atributo datetime
                datetime_attr = elemento.get('datetime')
                if datetime_attr:
                    fecha = self._parse_datetime_string(datetime_attr)
                    if fecha:
                        return fecha
                
                # Buscar en el texto del elemento
                texto = elemento.get_text(strip=True)
                fecha = self._parse_date_string(texto)
                if fecha:
                    return fecha
        
        return None
    
    def _extract_from_content(self, texto: str) -> Optional[datetime]:
        """Extraer fecha del contenido de texto"""
        # Buscar todos los patrones de fecha en el texto
        for patron in self.patrones:
            matches = re.finditer(patron, texto, re.IGNORECASE)
            for match in matches:
                fecha = self._parse_match(match)
                if fecha:
                    return fecha
        
        return None
    
    def _extract_from_url(self, url: str) -> Optional[datetime]:
        """Extraer fecha de la URL"""
        # Buscar patrones de fecha en la URL
        url_patrones = [
            r'/(\d{4})/(\d{1,2})/(\d{1,2})/',  # /2025/08/01/
            r'(\d{4})-(\d{1,2})-(\d{1,2})',    # 2025-08-01
            r'(\d{1,2})-(\d{1,2})-(\d{4})',    # 01-08-2025
        ]
        
        for patron in url_patrones:
            match = re.search(patron, url)
            if match:
                fecha = self._parse_match(match)
                if fecha:
                    return fecha
        
        return None
    
    def _extract_from_meta_tags(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extraer fecha de meta tags"""
        meta_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publish_date"]',
            'meta[name="date"]',
            'meta[name="pubdate"]',
            'meta[property="og:updated_time"]'
        ]
        
        for selector in meta_selectors:
            meta = soup.select_one(selector)
            if meta:
                content = meta.get('content')
                if content:
                    fecha = self._parse_datetime_string(content)
                    if fecha:
                        return fecha
        
        return None
    
    def _parse_match(self, match) -> Optional[datetime]:
        """Parsear un match de regex a datetime"""
        try:
            grupos = match.groups()
            
            if len(grupos) == 3:
                # Formato DD/MM/YYYY o DD-MM-YYYY
                if match.re.pattern == r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{4})':
                    dia, mes, año = int(grupos[0]), int(grupos[1]), int(grupos[2])
                    return datetime(año, mes, dia, tzinfo=timezone.utc)
                
                # Formato YYYY-MM-DD
                elif match.re.pattern == r'(\d{4})-(\d{1,2})-(\d{1,2})':
                    año, mes, dia = int(grupos[0]), int(grupos[1]), int(grupos[2])
                    return datetime(año, mes, dia, tzinfo=timezone.utc)
                
                # Formato DD de Mes de YYYY
                elif 'de' in match.re.pattern:
                    dia = int(grupos[0])
                    mes_texto = grupos[1].lower()
                    año = int(grupos[2])
                    
                    if mes_texto in self.meses:
                        return datetime(año, self.meses[mes_texto], dia, tzinfo=timezone.utc)
                
                # Formato Mes DD, YYYY
                elif match.re.pattern == r'(\w+)\s+(\d{1,2}),?\s+(\d{4})':
                    mes_texto = grupos[0].lower()
                    dia = int(grupos[1])
                    año = int(grupos[2])
                    
                    if mes_texto in self.meses:
                        return datetime(año, self.meses[mes_texto], dia, tzinfo=timezone.utc)
                
                # Formato DD Mes YYYY
                elif match.re.pattern == r'(\d{1,2})\s+(\w+)\s+(\d{4})':
                    dia = int(grupos[0])
                    mes_texto = grupos[1].lower()
                    año = int(grupos[2])
                    
                    if mes_texto in self.meses:
                        return datetime(año, self.meses[mes_texto], dia, tzinfo=timezone.utc)
                
                # Formato DD/MM/YY (año corto)
                elif match.re.pattern == r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2})':
                    dia, mes, año_corto = int(grupos[0]), int(grupos[1]), int(grupos[2])
                    año = 2000 + año_corto if año_corto < 50 else 1900 + año_corto
                    return datetime(año, mes, dia, tzinfo=timezone.utc)
            
            elif len(grupos) == 4:
                # Formato con día de la semana
                if match.re.pattern == r'(\w+),\s+(\d{1,2})\s+(\w+)\s+(\d{4})':
                    dia = int(grupos[1])
                    mes_texto = grupos[2].lower()
                    año = int(grupos[3])
                    
                    if mes_texto in self.meses:
                        return datetime(año, self.meses[mes_texto], dia, tzinfo=timezone.utc)
            
            elif len(grupos) == 6:
                # Formato ISO completo
                if match.re.pattern == r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})':
                    año, mes, dia = int(grupos[0]), int(grupos[1]), int(grupos[2])
                    hora, minuto, segundo = int(grupos[3]), int(grupos[4]), int(grupos[5])
                    return datetime(año, mes, dia, hora, minuto, segundo, tzinfo=timezone.utc)
        
        except (ValueError, IndexError) as e:
            print(f"⚠️ Error parseando fecha: {e}")
            return None
        
        return None
    
    def _parse_datetime_string(self, datetime_str: str) -> Optional[datetime]:
        """Parsear string de datetime ISO"""
        try:
            # Intentar parsear como ISO
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except ValueError:
            try:
                # Intentar otros formatos comunes
                for formato in [
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d %H:%M:%S%z',
                    '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%dT%H:%M:%SZ',
                    '%d/%m/%Y %H:%M:%S',
                    '%d-%m-%Y %H:%M:%S'
                ]:
                    try:
                        return datetime.strptime(datetime_str, formato)
                    except ValueError:
                        continue
            except Exception:
                pass
        
        return None
    
    def _parse_date_string(self, date_str: str) -> Optional[datetime]:
        """Parsear string de fecha usando patrones"""
        for patron in self.patrones:
            match = re.search(patron, date_str, re.IGNORECASE)
            if match:
                fecha = self._parse_match(match)
                if fecha:
                    return fecha
        return None

# Instancia global del extractor
date_extractor = UniversalDateExtractor() 
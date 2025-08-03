#!/usr/bin/env python3
"""
Script para actualizar todas las fuentes con el extractor universal de fechas
"""

import os
import sys
from pathlib import Path

def actualizar_scraper_con_extractor_universal(ruta_scraper: str):
    """Actualizar un scraper para usar el extractor universal de fechas"""
    
    print(f"🔧 Actualizando: {ruta_scraper}")
    
    try:
        with open(ruta_scraper, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar si ya tiene el import
        if 'from ..date_extractor import date_extractor' in contenido:
            print(f"  ✅ Ya tiene extractor universal")
            return False
        
        # Agregar import
        if 'from ..data_schema import' in contenido:
            contenido = contenido.replace(
                'from ..data_schema import',
                'from ..data_schema import\nfrom ..date_extractor import date_extractor'
            )
        elif 'from backend.processors.content_processor import' in contenido:
            contenido = contenido.replace(
                'from backend.processors.content_processor import',
                'from backend.processors.content_processor import\nfrom ..date_extractor import date_extractor'
            )
        
        # Buscar y reemplazar métodos de extracción de fecha
        cambios_realizados = []
        
        # Patrones comunes de métodos de fecha
        patrones_fecha = [
            r'def _extract_fecha_.*?\(.*?\):\s*""".*?"""\s*.*?return datetime\.now\(\)',
            r'def extraer_fecha_.*?\(.*?\):\s*""".*?"""\s*.*?return datetime\.now\(\)',
            r'def _parse_fecha_.*?\(.*?\):\s*""".*?"""\s*.*?return datetime\.now\(\)'
        ]
        
        for patron in patrones_fecha:
            if re.search(patron, contenido, re.DOTALL):
                # Reemplazar con método simplificado
                nuevo_metodo = '''    def _extract_fecha_universal(self, soup: BeautifulSoup, url: str = None) -> datetime:
        """Extraer fecha usando extractor universal"""
        try:
            fecha = date_extractor.extract_date_from_html(soup, url)
            if fecha:
                return fecha
            return datetime.now(timezone.utc)
        except Exception as e:
            print(f"⚠️ Error extrayendo fecha: {e}")
            return datetime.now(timezone.utc)'''
                
                contenido = re.sub(patron, nuevo_metodo, contenido, flags=re.DOTALL)
                cambios_realizados.append("método de fecha")
        
        # Buscar llamadas a métodos de fecha y actualizarlas
        if 'self._extract_fecha_' in contenido:
            contenido = contenido.replace('self._extract_fecha_', 'self._extract_fecha_universal')
            cambios_realizados.append("llamadas a método")
        
        if 'self.extraer_fecha_' in contenido:
            contenido = contenido.replace('self.extraer_fecha_', 'self._extract_fecha_universal')
            cambios_realizados.append("llamadas a método")
        
        # Guardar cambios
        if cambios_realizados:
            with open(ruta_scraper, 'w', encoding='utf-8') as f:
                f.write(contenido)
            print(f"  ✅ Actualizado: {', '.join(cambios_realizados)}")
            return True
        else:
            print(f"  ⚠️ No se encontraron métodos de fecha para actualizar")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Actualizar todos los scrapers"""
    
    print("🔄 ACTUALIZANDO TODAS LAS FUENTES CON EXTRACTOR UNIVERSAL DE FECHAS")
    print("=" * 80)
    
    # Directorio de scrapers
    scrapers_dir = Path("backend/scrapers/fuentes")
    
    # Lista de scrapers a actualizar
    scrapers_a_actualizar = [
        "sii/sii_scraper.py",
        "inapi/inapi_scraper.py", 
        "contraloria/contraloria_scraper.py",
        "tdlc/tdlc_scraper.py",
        "1ta/1ta_scraper.py",
        "tdpi/tdpi_scraper.py",
        "ministerio_justicia/ministerio_justicia_scraper.py"
    ]
    
    actualizados = 0
    total = len(scrapers_a_actualizar)
    
    for scraper in scrapers_a_actualizar:
        ruta = scrapers_dir / scraper
        if ruta.exists():
            if actualizar_scraper_con_extractor_universal(str(ruta)):
                actualizados += 1
        else:
            print(f"❌ No encontrado: {scraper}")
    
    print(f"\n📊 RESUMEN:")
    print(f"  ✅ Actualizados: {actualizados}/{total}")
    print(f"  📋 Fuentes con extractor universal: {actualizados}")
    
    if actualizados > 0:
        print(f"\n🎯 PRÓXIMO PASO:")
        print(f"  Ejecuta: python3 backend/main.py --once --max-noticias 5")
        print(f"  Para probar todas las fuentes con fechas corregidas")

if __name__ == "__main__":
    import re
    main() 
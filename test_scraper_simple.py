#!/usr/bin/env python3
"""
Scraper simple de prueba para verificar la estructura
"""
import sys
import os
from typing import List, Dict, Optional
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import requests
import re
sys.path.append(os.path.dirname(__file__))

from backend.scrapers.fuentes.data_schema import (
    NoticiaEstandarizada,
    Categoria,
    Jurisdiccion,
    TipoDocumento
)

class ScraperSimple:
    """Scraper simple para pruebas"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def test_tdlc(self):
        """Probar TDLC"""
        print("🧪 Probando TDLC...")
        try:
            response = self.session.get("https://www.tdlc.cl/noticias/", timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar noticias
            noticias = []
            fecha_pattern = re.compile(r'\d{2}/\d{2}/\d{4}')
            
            # Buscar bloques de texto que contengan fechas
            for elemento in soup.find_all(['div', 'p']):
                texto = elemento.get_text(strip=True)
                if fecha_pattern.search(texto) and len(texto) > 50:
                    fecha_match = fecha_pattern.search(texto)
                    fecha = fecha_match.group()
                    titulo = texto[len(fecha):].strip()[:100]
                    
                    noticias.append({
                        'titulo': titulo,
                        'fecha': fecha,
                        'url': 'https://www.tdlc.cl/noticias/',
                        'contenido': texto[:200]
                    })
            
            print(f"✅ TDLC: {len(noticias)} noticias encontradas")
            if noticias:
                print(f"   Primera: {noticias[0]['titulo']}")
            return noticias
            
        except Exception as e:
            print(f"❌ Error TDLC: {str(e)}")
            return []

    def test_3ta(self):
        """Probar 3TA"""
        print("🧪 Probando 3TA...")
        try:
            response = self.session.get("https://3ta.cl/category/noticias/", timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar enlaces de noticias
            noticias = []
            enlaces = soup.find_all('a', href=True)
            
            for enlace in enlaces:
                href = enlace['href']
                if 'noticias' in href or 'news' in href:
                    titulo = enlace.get_text(strip=True)
                    if titulo and len(titulo) > 10:
                        noticias.append({
                            'titulo': titulo,
                            'fecha': '',
                            'url': href if href.startswith('http') else f"https://3ta.cl{href}",
                            'contenido': ''
                        })
            
            print(f"✅ 3TA: {len(noticias)} noticias encontradas")
            if noticias:
                print(f"   Primera: {noticias[0]['titulo']}")
            return noticias
            
        except Exception as e:
            print(f"❌ Error 3TA: {str(e)}")
            return []

def main():
    """Función principal"""
    print("🚀 PRUEBA SIMPLE DE SCRAPERS")
    print("="*50)
    
    scraper = ScraperSimple()
    
    # Probar TDLC
    tdlc_noticias = scraper.test_tdlc()
    
    # Probar 3TA
    t3ta_noticias = scraper.test_3ta()
    
    print(f"\n📊 RESUMEN:")
    print(f"   TDLC: {len(tdlc_noticias)} noticias")
    print(f"   3TA: {len(t3ta_noticias)} noticias")
    print(f"   Total: {len(tdlc_noticias) + len(t3ta_noticias)} noticias")

if __name__ == "__main__":
    main() 
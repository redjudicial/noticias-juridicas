#!/usr/bin/env python3
"""
Script para investigar la estructura de la página del Ministerio de Justicia
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def investigar_ministerio_justicia():
    """Investigar la página del Ministerio de Justicia"""
    url = "https://www.minjusticia.gob.cl/category/noticias/"
    
    print(f"🔍 Investigando: {url}")
    
    try:
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            print("\n📰 Enlaces encontrados:")
            
            # Buscar todos los enlaces
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text(strip=True)
                
                if text and len(text) > 5:  # Filtrar textos muy cortos
                    full_url = urljoin(url, href)
                    print(f"   - {text[:50]}... -> {full_url}")
            
            print(f"\n📊 Total de enlaces: {len(soup.find_all('a', href=True))}")
            
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    investigar_ministerio_justicia() 
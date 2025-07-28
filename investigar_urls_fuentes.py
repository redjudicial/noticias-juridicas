#!/usr/bin/env python3
"""
Script para investigar las URLs correctas de las fuentes de noticias jurídicas
"""

import requests
from bs4 import BeautifulSoup
import feedparser
from urllib.parse import urljoin, urlparse

def test_url(url, descripcion):
    """Probar una URL y mostrar el resultado"""
    print(f"\n🔍 Probando: {descripcion}")
    print(f"   URL: {url}")
    
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ URL válida")
            
            # Si es HTML, buscar enlaces de noticias
            if 'text/html' in response.headers.get('content-type', ''):
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Buscar enlaces que contengan palabras clave de noticias
                noticia_links = []
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    text = link.get_text(strip=True).lower()
                    
                    if any(keyword in text for keyword in ['noticia', 'prensa', 'comunicado', 'novedad']):
                        full_url = urljoin(url, href)
                        noticia_links.append((text, full_url))
                
                if noticia_links:
                    print(f"   📰 Enlaces de noticias encontrados:")
                    for text, link_url in noticia_links[:5]:  # Mostrar solo los primeros 5
                        print(f"      - {text[:50]}... -> {link_url}")
                else:
                    print(f"   ⚠️  No se encontraron enlaces de noticias")
            
            # Si es RSS, parsear el feed
            elif 'xml' in response.headers.get('content-type', '') or 'rss' in response.headers.get('content-type', ''):
                feed = feedparser.parse(response.content)
                print(f"   📰 RSS válido: {len(feed.entries)} entradas")
                if feed.entries:
                    print(f"   📄 Primera entrada: {feed.entries[0].get('title', 'Sin título')}")
        
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def investigar_fuentes():
    """Investigar todas las fuentes"""
    print("🔍 INVESTIGACIÓN DE URLs DE FUENTES JURÍDICAS")
    print("=" * 60)
    
    # Poder Judicial
    test_url("https://www.pjud.cl", "Poder Judicial - Página principal")
    test_url("https://www.pjud.cl/prensa-y-comunicaciones", "Poder Judicial - Prensa")
    test_url("https://www.pjud.cl/noticias", "Poder Judicial - Noticias")
    
    # Tribunal Constitucional
    test_url("https://www.tribunalconstitucional.cl", "Tribunal Constitucional - Página principal")
    test_url("https://www.tribunalconstitucional.cl/prensa", "Tribunal Constitucional - Prensa")
    test_url("https://www.tribunalconstitucional.cl/noticias", "Tribunal Constitucional - Noticias")
    
    # Defensoría Penal Pública
    test_url("https://www.dpp.cl", "DPP - Página principal")
    test_url("https://www.dpp.cl/sala-de-prensa", "DPP - Sala de prensa")
    test_url("https://www.dpp.cl/noticias", "DPP - Noticias")
    
    # Diario Oficial
    test_url("https://www.diariooficial.interior.gob.cl", "Diario Oficial - Página principal")
    test_url("https://www.diariooficial.interior.gob.cl/publicaciones", "Diario Oficial - Publicaciones")
    
    # Ministerio de Justicia
    test_url("https://www.minjusticia.gob.cl", "Ministerio de Justicia - Página principal")
    test_url("https://www.minjusticia.gob.cl/feed", "Ministerio de Justicia - RSS")
    test_url("https://www.minjusticia.gob.cl/noticias", "Ministerio de Justicia - Noticias")
    
    # Fiscalía
    test_url("https://www.fiscaliadechile.cl", "Fiscalía - Página principal")
    test_url("https://www.fiscaliadechile.cl/feed", "Fiscalía - RSS")
    test_url("https://www.fiscaliadechile.cl/noticias", "Fiscalía - Noticias")
    
    # Contraloría
    test_url("https://www.contraloria.cl", "Contraloría - Página principal")
    test_url("https://www.contraloria.cl/feed", "Contraloría - RSS")
    test_url("https://www.contraloria.cl/noticias", "Contraloría - Noticias")
    
    # CDE
    test_url("https://www.cde.cl", "CDE - Página principal")
    test_url("https://www.cde.cl/feed", "CDE - RSS")
    test_url("https://www.cde.cl/noticias", "CDE - Noticias")

if __name__ == "__main__":
    investigar_fuentes() 
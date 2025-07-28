#!/usr/bin/env python3
"""
Script para investigar la estructura de la página de CDE
"""

import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import re

def investigar_cde():
    """Investigar la estructura de la página de CDE"""
    sitemap_url = "https://www.cde.cl/post-sitemap1.xml"
    main_url = "https://www.cde.cl"
    
    try:
        print("🔍 INVESTIGANDO ESTRUCTURA DE CDE")
        print("=" * 60)
        
        # Probar sitemap
        print("📄 PROBANDO SITEMAP:")
        print("-" * 40)
        
        try:
            response = requests.get(sitemap_url, timeout=30)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            urls = root.findall('.//ns:url', namespace)
            print(f"📊 URLs en sitemap: {len(urls)}")
            
            # Mostrar primeras URLs
            for i, url_elem in enumerate(urls[:10], 1):
                loc_elem = url_elem.find('ns:loc', namespace)
                if loc_elem is not None:
                    url = loc_elem.text
                    print(f"   {i}. {url}")
            
        except Exception as e:
            print(f"❌ Error con sitemap: {e}")
        
        # Probar página principal
        print("\n🌐 PROBANDO PÁGINA PRINCIPAL:")
        print("-" * 40)
        
        try:
            response = requests.get(main_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            print(f"📄 Título de la página: {soup.title.string if soup.title else 'Sin título'}")
            print(f"📊 Tamaño del contenido: {len(response.content)} bytes")
            
            # Buscar enlaces
            links = soup.find_all('a', href=True)
            print(f"🔗 Enlaces encontrados: {len(links)}")
            
            # Buscar enlaces de noticias
            noticia_links = []
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if (href and 
                    text and 
                    len(text) > 5 and
                    ('noticia' in text.lower() or 'news' in text.lower() or 'comunicado' in text.lower())):
                    
                    noticia_links.append({
                        'href': href,
                        'text': text,
                        'full_url': href if href.startswith('http') else f"{main_url}{href}"
                    })
            
            print(f"📰 Enlaces de noticias encontrados: {len(noticia_links)}")
            for i, link in enumerate(noticia_links[:5], 1):
                print(f"   {i}. {link['text'][:60]}...")
                print(f"      URL: {link['full_url']}")
                print()
            
        except Exception as e:
            print(f"❌ Error con página principal: {e}")
        
        # Probar diferentes URLs de noticias
        print("🔍 PROBANDO URLs DE NOTICIAS:")
        print("-" * 40)
        
        test_urls = [
            "https://www.cde.cl/noticias/",
            "https://www.cde.cl/news/",
            "https://www.cde.cl/comunicados/",
            "https://www.cde.cl/actualidad/",
            "https://www.cde.cl/prensa/"
        ]
        
        for test_url in test_urls:
            try:
                response = requests.get(test_url, timeout=10)
                print(f"✅ {test_url}: {response.status_code}")
            except Exception as e:
                print(f"❌ {test_url}: {e}")
        
    except Exception as e:
        print(f"❌ Error investigando CDE: {e}")

if __name__ == "__main__":
    investigar_cde() 
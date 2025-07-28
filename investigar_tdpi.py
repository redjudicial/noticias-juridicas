#!/usr/bin/env python3
"""
Script para investigar la estructura de la página de TDPI
"""

import requests
from bs4 import BeautifulSoup
import re

def investigar_tdpi():
    """Investigar la estructura de la página de TDPI"""
    url = "https://www.tdpi.cl/category/noticias/"
    
    try:
        print("🔍 INVESTIGANDO ESTRUCTURA DE TDPI")
        print("=" * 60)
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"📄 Título de la página: {soup.title.string if soup.title else 'Sin título'}")
        print(f"📊 Tamaño del contenido: {len(response.content)} bytes")
        print()
        
        # Buscar todos los enlaces
        print("🔗 ENLACES ENCONTRADOS:")
        print("-" * 40)
        
        links = soup.find_all('a', href=True)
        noticia_links = []
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Filtrar enlaces de noticias
            if (href and 
                text and 
                len(text) > 10 and
                not any(excl in text.lower() for excl in ['inicio', 'menu', 'contacto', 'transparencia', 'página', 'anterior', 'siguiente'])):
                
                noticia_links.append({
                    'href': href,
                    'text': text,
                    'full_url': href if href.startswith('http') else f"https://www.tdpi.cl{href}"
                })
        
        print(f"📰 Enlaces encontrados: {len(noticia_links)}")
        for i, link in enumerate(noticia_links[:10], 1):
            print(f"   {i}. {link['text'][:80]}...")
            print(f"      URL: {link['full_url']}")
            print()
        
        # Buscar elementos específicos
        print("🔍 ELEMENTOS ESPECÍFICOS:")
        print("-" * 40)
        
        # Buscar artículos
        articles = soup.find_all('article')
        print(f"📄 Artículos encontrados: {len(articles)}")
        
        # Buscar posts
        posts = soup.find_all(class_=re.compile(r'post|entry|noticia'))
        print(f"📝 Posts encontrados: {len(posts)}")
        
        # Buscar títulos
        titles = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        print(f"📋 Títulos encontrados: {len(titles)}")
        for i, title in enumerate(titles[:5], 1):
            print(f"   {i}. {title.get_text(strip=True)[:60]}...")
        
        # Buscar contenido
        content_divs = soup.find_all('div', class_=re.compile(r'content|entry|post|noticia'))
        print(f"📄 Divs de contenido encontrados: {len(content_divs)}")
        
    except Exception as e:
        print(f"❌ Error investigando TDPI: {e}")

if __name__ == "__main__":
    investigar_tdpi() 
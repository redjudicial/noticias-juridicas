#!/usr/bin/env python3
"""
Script para investigar la estructura real de la página de Contraloría
"""

import requests
from bs4 import BeautifulSoup
import re

def investigar_contraloria():
    """Investigar la estructura de la página de Contraloría"""
    url = "https://www.contraloria.cl/portalweb/web/cgr/noticias"
    
    try:
        print("🔍 INVESTIGANDO ESTRUCTURA DE CONTRALORÍA")
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
                ('noticias' in href.lower() or 'content' in href.lower()) and
                not any(excl in text.lower() for excl in ['inicio', 'menu', 'contacto', 'transparencia', 'página', 'anterior', 'siguiente'])):
                
                noticia_links.append({
                    'href': href,
                    'text': text,
                    'full_url': href if href.startswith('http') else f"https://www.contraloria.cl{href}"
                })
        
        print(f"📰 Enlaces de noticias encontrados: {len(noticia_links)}")
        for i, link in enumerate(noticia_links[:5], 1):
            print(f"   {i}. {link['text'][:80]}...")
            print(f"      URL: {link['full_url']}")
            print()
        
        # Probar extraer contenido de una noticia
        if noticia_links:
            test_url = noticia_links[0]['full_url']
            print(f"🧪 PROBANDO EXTRACCIÓN DE CONTENIDO:")
            print(f"URL de prueba: {test_url}")
            print("-" * 40)
            
            try:
                test_response = requests.get(test_url, timeout=30)
                test_response.raise_for_status()
                
                test_soup = BeautifulSoup(test_response.content, 'html.parser')
                
                print(f"📄 Título de la noticia: {test_soup.title.string if test_soup.title else 'Sin título'}")
                print(f"📊 Tamaño del contenido: {len(test_response.content)} bytes")
                
                # Buscar contenido
                content_selectors = [
                    '.entry-content',
                    '.post-content',
                    '.noticia-contenido',
                    '.content',
                    'article',
                    '.main-content',
                    '.noticia-body',
                    '.journal-content-article',
                    '.portlet-body',
                    '.asset-content'
                ]
                
                print("\n🔍 BUSCANDO CONTENIDO:")
                for selector in content_selectors:
                    elem = test_soup.select_one(selector)
                    if elem:
                        text = elem.get_text(strip=True)
                        print(f"✅ Selector '{selector}': {len(text)} caracteres")
                        print(f"   Primeros 200 caracteres: {text[:200]}...")
                        break
                else:
                    print("❌ No se encontró contenido con los selectores estándar")
                    
                    # Buscar cualquier div con contenido
                    divs = test_soup.find_all('div')
                    for div in divs:
                        text = div.get_text(strip=True)
                        if len(text) > 500:  # Contenido sustancial
                            classes = ' '.join(div.get('class', []))
                            print(f"📝 Div con clase '{classes}': {len(text)} caracteres")
                            print(f"   Primeros 200 caracteres: {text[:200]}...")
                            break
                
            except Exception as e:
                print(f"❌ Error accediendo a la noticia: {e}")
        
    except Exception as e:
        print(f"❌ Error investigando Contraloría: {e}")

if __name__ == "__main__":
    investigar_contraloria() 
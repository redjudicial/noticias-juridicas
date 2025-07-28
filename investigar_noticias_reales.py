#!/usr/bin/env python3
"""
Script para investigar noticias reales en las páginas que funcionan
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def investigar_noticias_poder_judicial():
    """Investigar noticias reales del Poder Judicial"""
    print("🔍 INVESTIGANDO NOTICIAS REALES - PODER JUDICIAL")
    print("=" * 60)
    
    url = "https://www.pjud.cl/prensa-y-comunicaciones/noticias-del-poder-judicial"
    
    try:
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar todos los enlaces
            enlaces = soup.find_all('a', href=True)
            
            print(f"📊 Total de enlaces: {len(enlaces)}")
            
            # Buscar enlaces que parezcan noticias
            noticias = []
            for link in enlaces:
                href = link.get('href')
                text = link.get_text(strip=True)
                
                # Filtrar enlaces que parezcan noticias
                if (text and len(text) > 20 and 
                    not any(exclusion in text.lower() for exclusion in ['inicio', 'menu', 'siguiente', 'anterior']) and
                    not any(exclusion in href.lower() for exclusion in ['#', 'javascript:', 'mailto:'])):
                    
                    full_url = urljoin(url, href)
                    noticias.append((text, full_url))
            
            print(f"📰 Enlaces potenciales de noticias: {len(noticias)}")
            for i, (text, url) in enumerate(noticias[:10], 1):
                print(f"   {i}. {text[:80]}...")
                print(f"      URL: {url}")
                print()
        
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def investigar_noticias_dpp():
    """Investigar noticias reales de la DPP"""
    print("\n🔍 INVESTIGANDO NOTICIAS REALES - DPP")
    print("=" * 60)
    
    url = "https://www.dpp.cl/sala_prensa/noticias"
    
    try:
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar todos los enlaces
            enlaces = soup.find_all('a', href=True)
            
            print(f"📊 Total de enlaces: {len(enlaces)}")
            
            # Buscar enlaces que parezcan noticias
            noticias = []
            for link in enlaces:
                href = link.get('href')
                text = link.get_text(strip=True)
                
                # Filtrar enlaces que parezcan noticias
                if (text and len(text) > 20 and 
                    not any(exclusion in text.lower() for exclusion in ['inicio', 'menu', 'siguiente', 'anterior']) and
                    not any(exclusion in href.lower() for exclusion in ['#', 'javascript:', 'mailto:'])):
                    
                    full_url = urljoin(url, href)
                    noticias.append((text, full_url))
            
            print(f"📰 Enlaces potenciales de noticias: {len(noticias)}")
            for i, (text, url) in enumerate(noticias[:10], 1):
                print(f"   {i}. {text[:80]}...")
                print(f"      URL: {url}")
                print()
        
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def investigar_tribunal_constitucional_alternativo():
    """Investigar Tribunal Constitucional con URLs alternativas"""
    print("\n🔍 INVESTIGANDO TRIBUNAL CONSTITUCIONAL - URLs ALTERNATIVAS")
    print("=" * 60)
    
    urls = [
        "https://www.tribunalconstitucional.cl",
        "https://www.tribunalconstitucional.cl/prensa",
        "https://www.tribunalconstitucional.cl/comunicados"
    ]
    
    for url in urls:
        print(f"\n🔍 Probando: {url}")
        try:
            response = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Buscar enlaces que parezcan noticias
                enlaces = soup.find_all('a', href=True)
                noticias = []
                
                for link in enlaces:
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    
                    if (text and len(text) > 20 and 
                        any(keyword in text.lower() for keyword in ['noticia', 'comunicado', 'fallo', 'sentencia', 'resolución'])):
                        
                        full_url = urljoin(url, href)
                        noticias.append((text, full_url))
                
                print(f"📰 Enlaces de noticias encontrados: {len(noticias)}")
                for i, (text, url) in enumerate(noticias[:3], 1):
                    print(f"   {i}. {text[:60]}...")
            
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Función principal"""
    investigar_noticias_poder_judicial()
    investigar_noticias_dpp()
    investigar_tribunal_constitucional_alternativo()

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Script para investigar problemas específicos de cada fuente
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def investigar_poder_judicial():
    """Investigar Poder Judicial"""
    print("🔍 INVESTIGANDO PODER JUDICIAL")
    print("=" * 50)
    
    url = "https://www.pjud.cl/prensa-y-comunicaciones/noticias-del-poder-judicial"
    
    try:
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar enlaces específicos
            enlaces = soup.find_all('a', href=True)
            noticias = []
            
            for link in enlaces:
                href = link.get('href')
                text = link.get_text(strip=True)
                
                if text and len(text) > 10 and any(keyword in text.lower() for keyword in ['noticia', 'comunicado', 'fallo', 'sentencia']):
                    full_url = urljoin(url, href)
                    noticias.append((text, full_url))
            
            print(f"📰 Enlaces de noticias encontrados: {len(noticias)}")
            for i, (text, url) in enumerate(noticias[:5], 1):
                print(f"   {i}. {text[:60]}... -> {url}")
        
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def investigar_dpp():
    """Investigar DPP"""
    print("\n🔍 INVESTIGANDO DPP")
    print("=" * 50)
    
    url = "https://www.dpp.cl/sala_prensa/noticias"
    
    try:
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar enlaces específicos
            enlaces = soup.find_all('a', href=True)
            noticias = []
            
            for link in enlaces:
                href = link.get('href')
                text = link.get_text(strip=True)
                
                if text and len(text) > 10 and any(keyword in text.lower() for keyword in ['noticia', 'comunicado', 'prensa']):
                    full_url = urljoin(url, href)
                    noticias.append((text, full_url))
            
            print(f"📰 Enlaces de noticias encontrados: {len(noticias)}")
            for i, (text, url) in enumerate(noticias[:5], 1):
                print(f"   {i}. {text[:60]}... -> {url}")
        
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def investigar_tribunal_constitucional():
    """Investigar Tribunal Constitucional"""
    print("\n🔍 INVESTIGANDO TRIBUNAL CONSTITUCIONAL")
    print("=" * 50)
    
    url = "https://www.tribunalconstitucional.cl/noticias"
    
    try:
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar enlaces específicos
            enlaces = soup.find_all('a', href=True)
            noticias = []
            
            for link in enlaces:
                href = link.get('href')
                text = link.get_text(strip=True)
                
                if text and len(text) > 10 and any(keyword in text.lower() for keyword in ['noticia', 'comunicado', 'fallo', 'sentencia']):
                    full_url = urljoin(url, href)
                    noticias.append((text, full_url))
            
            print(f"📰 Enlaces de noticias encontrados: {len(noticias)}")
            for i, (text, url) in enumerate(noticias[:5], 1):
                print(f"   {i}. {text[:60]}... -> {url}")
        
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def investigar_fiscalia():
    """Investigar Fiscalía"""
    print("\n🔍 INVESTIGANDO FISCALÍA")
    print("=" * 50)
    
    url = "https://www.fiscaliadechile.cl"
    
    try:
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar enlaces específicos
            enlaces = soup.find_all('a', href=True)
            noticias = []
            
            for link in enlaces:
                href = link.get('href')
                text = link.get_text(strip=True)
                
                if text and len(text) > 10 and any(keyword in text.lower() for keyword in ['noticia', 'comunicado', 'prensa']):
                    full_url = urljoin(url, href)
                    noticias.append((text, full_url))
            
            print(f"📰 Enlaces de noticias encontrados: {len(noticias)}")
            for i, (text, url) in enumerate(noticias[:5], 1):
                print(f"   {i}. {text[:60]}... -> {url}")
        
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal"""
    investigar_poder_judicial()
    investigar_dpp()
    investigar_tribunal_constitucional()
    investigar_fiscalia()

if __name__ == "__main__":
    main() 
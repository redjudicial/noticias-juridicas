#!/usr/bin/env python3
"""
Script de prueba específico para el Ministerio de Justicia
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(__file__))

from backend.scrapers.rss_scrapers import MinisterioJusticiaScraper

def test_ministerio_justicia():
    """Probar scraper del Ministerio de Justicia"""
    print("🔍 Probando scraper del Ministerio de Justicia")
    print("=" * 50)
    
    scraper = MinisterioJusticiaScraper(openai_api_key=os.getenv('OPENAI_API_KEY'))
    
    # Probar obtención de noticias
    print("📰 Obteniendo noticias...")
    noticias = scraper.get_noticias_from_web("https://www.minjusticia.gob.cl/category/noticias/", 10)
    
    print(f"✅ Encontradas {len(noticias)} noticias")
    
    for i, noticia in enumerate(noticias, 1):
        print(f"\n📄 Noticia {i}:")
        print(f"   Título: {noticia['titulo']}")
        print(f"   URL: {noticia['url']}")
        print(f"   Fecha: {noticia['fecha']}")
    
    # Probar extracción de una noticia completa
    if noticias:
        print(f"\n🔍 Extrayendo noticia completa de: {noticias[0]['url']}")
        noticia_completa = scraper.get_noticia_completa(
            noticias[0]['url'],
            noticias[0]['titulo']
        )
        
        if noticia_completa:
            print(f"✅ Noticia extraída exitosamente")
            print(f"   Título: {noticia_completa.titulo}")
            print(f"   Contenido: {len(noticia_completa.cuerpo_completo)} caracteres")
            print(f"   Fuente: {noticia_completa.fuente}")
        else:
            print("❌ Error extrayendo noticia completa")

if __name__ == "__main__":
    test_ministerio_justicia() 
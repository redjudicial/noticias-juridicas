#!/usr/bin/env python3
"""
Script de prueba para el scraper del SII
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.scrapers.fuentes.sii import SIIScraper

def test_sii_scraper():
    """Probar el scraper del SII"""
    print("🧪 PRUEBA DEL SCRAPER SII")
    print("=" * 50)
    
    try:
        # Inicializar scraper
        scraper = SIIScraper(
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        print("✅ Scraper SII inicializado")
        
        # Probar obtener lista de noticias
        print("\n🔍 Probando obtener lista de noticias...")
        noticias_raw = scraper.get_noticias_recientes(max_noticias=5)
        
        if noticias_raw:
            print(f"✅ Encontradas {len(noticias_raw)} noticias:")
            for i, noticia in enumerate(noticias_raw[:3], 1):
                print(f"  {i}. {noticia['titulo'][:80]}...")
                print(f"     URL: {noticia['url']}")
                print(f"     Fecha: {noticia['fecha']}")
                print()
        else:
            print("❌ No se encontraron noticias")
            return
        
        # Probar extraer noticia completa
        print("🔍 Probando extraer noticia completa...")
        if noticias_raw:
            primera_noticia = noticias_raw[0]
            noticia_completa = scraper.get_noticia_completa(
                url=primera_noticia['url'],
                titulo=primera_noticia['titulo'],
                fecha_str=primera_noticia.get('fecha')
            )
            
            if noticia_completa:
                print("✅ Noticia completa extraída:")
                print(f"  Título: {noticia_completa.titulo}")
                print(f"  Fuente: {noticia_completa.fuente}")
                print(f"  Categoría: {noticia_completa.categoria}")
                print(f"  Contenido: {noticia_completa.cuerpo_completo[:200]}...")
                print(f"  Fecha: {noticia_completa.fecha_publicacion}")
            else:
                print("❌ No se pudo extraer la noticia completa")
        
        # Probar scraping completo
        print("\n🔍 Probando scraping completo...")
        noticias_procesadas = scraper.scrape_noticias_recientes(max_noticias=3)
        
        if noticias_procesadas:
            print(f"✅ Scraping completo exitoso: {len(noticias_procesadas)} noticias procesadas")
            for i, noticia in enumerate(noticias_procesadas, 1):
                print(f"  {i}. {noticia.titulo[:60]}...")
        else:
            print("❌ Scraping completo falló")
        
        print("\n🎯 PRUEBA COMPLETADA")
        
    except Exception as e:
        print(f"❌ Error en la prueba: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sii_scraper() 
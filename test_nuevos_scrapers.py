#!/usr/bin/env python3
"""
Script de prueba para los 4 nuevos scrapers: SII, TTA, INAPI y DT
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.scrapers.fuentes.sii import SIIScraper
from backend.scrapers.fuentes.tta import TTAScraper
from backend.scrapers.fuentes.inapi import INAPIScraper
from backend.scrapers.fuentes.dt import DTScraper

def test_scraper(scraper_class, nombre):
    """Probar un scraper específico"""
    print(f"\n🧪 PROBANDO SCRAPER {nombre}")
    print("=" * 60)
    
    try:
        # Inicializar scraper
        scraper = scraper_class(
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        print(f"✅ Scraper {nombre} inicializado")
        
        # Probar obtener lista de noticias
        print(f"\n🔍 Probando obtener lista de noticias de {nombre}...")
        noticias_raw = scraper.get_noticias_recientes(max_noticias=3)
        
        if noticias_raw:
            print(f"✅ Encontradas {len(noticias_raw)} noticias:")
            for i, noticia in enumerate(noticias_raw, 1):
                print(f"  {i}. {noticia['titulo'][:80]}...")
                print(f"     URL: {noticia['url']}")
                print(f"     Fecha: {noticia['fecha']}")
                print()
        else:
            print(f"❌ No se encontraron noticias de {nombre}")
            return
        
        # Probar extraer noticia completa
        print(f"🔍 Probando extraer noticia completa de {nombre}...")
        if noticias_raw:
            primera_noticia = noticias_raw[0]
            noticia_completa = scraper.get_noticia_completa(
                url=primera_noticia['url'],
                titulo=primera_noticia['titulo'],
                fecha_str=primera_noticia.get('fecha')
            )
            
            if noticia_completa:
                print(f"✅ Noticia completa extraída de {nombre}:")
                print(f"  Título: {noticia_completa.titulo}")
                print(f"  Fuente: {noticia_completa.fuente}")
                print(f"  Categoría: {noticia_completa.categoria}")
                print(f"  Contenido: {noticia_completa.cuerpo_completo[:200]}...")
                print(f"  Fecha: {noticia_completa.fecha_publicacion}")
            else:
                print(f"❌ No se pudo extraer la noticia completa de {nombre}")
        
        print(f"\n🎯 PRUEBA DE {nombre} COMPLETADA")
        
    except Exception as e:
        print(f"❌ Error en la prueba de {nombre}: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Ejecutar todas las pruebas"""
    print("🚀 PRUEBAS DE LOS 4 NUEVOS SCRAPERS")
    print("=" * 80)
    
    scrapers_test = [
        (SIIScraper, "SII"),
        (TTAScraper, "TTA"),
        (INAPIScraper, "INAPI"),
        (DTScraper, "DT")
    ]
    
    resultados = []
    
    for scraper_class, nombre in scrapers_test:
        try:
            test_scraper(scraper_class, nombre)
            resultados.append(f"✅ {nombre}: EXITOSO")
        except Exception as e:
            resultados.append(f"❌ {nombre}: ERROR - {str(e)}")
    
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE RESULTADOS:")
    print("=" * 80)
    
    for resultado in resultados:
        print(resultado)
    
    exitosos = len([r for r in resultados if "✅" in r])
    print(f"\n🎯 SCRAPERS EXITOSOS: {exitosos}/4")

if __name__ == "__main__":
    main() 
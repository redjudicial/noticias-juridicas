#!/usr/bin/env python3
"""
Script para probar las 4 nuevas fuentes implementadas:
- TDLC (Tribunal de Defensa de la Libre Competencia)
- 1TA (Primer Tribunal Ambiental)
- 3TA (Tercer Tribunal Ambiental)
- Tribunal Ambiental General
"""
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(__file__))

from backend.scrapers.fuentes import (
    TDLScraper,
    PrimerTribunalAmbientalScraper,
    TercerTribunalAmbientalScraper,
    TribunalAmbientalScraper
)

def test_scraper(scraper_class, nombre):
    """Prueba un scraper específico"""
    print(f"\n{'='*60}")
    print(f"🧪 PROBANDO: {nombre}")
    print(f"{'='*60}")
    
    try:
        scraper = scraper_class()
        noticias_raw = scraper.get_noticias_recientes(max_noticias=5)
        
        print(f"📊 Noticias encontradas: {len(noticias_raw)}")
        
        if noticias_raw:
            print(f"\n📰 PRIMERA NOTICIA:")
            primera = noticias_raw[0]
            print(f"   Título: {primera.get('titulo', 'N/A')}")
            print(f"   Fecha: {primera.get('fecha', 'N/A')}")
            print(f"   URL: {primera.get('url', 'N/A')}")
            print(f"   Contenido: {primera.get('contenido', 'N/A')[:100]}...")
            
            # Procesar la primera noticia
            noticia_procesada = scraper.procesar_noticia(primera)
            if noticia_procesada:
                print(f"\n✅ NOTICIA PROCESADA:")
                print(f"   Título: {noticia_procesada.titulo}")
                print(f"   Fuente: {noticia_procesada.fuente}")
                print(f"   Categoría: {noticia_procesada.categoria}")
                print(f"   Palabras clave: {noticia_procesada.palabras_clave}")
            else:
                print(f"❌ Error procesando noticia")
        else:
            print(f"❌ No se encontraron noticias")
            
    except Exception as e:
        print(f"❌ Error en {nombre}: {str(e)}")

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DE NUEVAS FUENTES")
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Lista de scrapers a probar
    scrapers = [
        (TDLScraper, "TDLC - Tribunal de Defensa de la Libre Competencia"),
        (PrimerTribunalAmbientalScraper, "1TA - Primer Tribunal Ambiental"),
        (TercerTribunalAmbientalScraper, "3TA - Tercer Tribunal Ambiental"),
        (TribunalAmbientalScraper, "Tribunal Ambiental General")
    ]
    
    # Probar cada scraper
    for scraper_class, nombre in scrapers:
        test_scraper(scraper_class, nombre)
    
    print(f"\n{'='*60}")
    print("🏁 PRUEBAS COMPLETADAS")
    print(f"{'='*60}")

if __name__ == "__main__":
    main() 
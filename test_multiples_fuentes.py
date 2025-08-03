#!/usr/bin/env python3
"""
Script para probar múltiples fuentes específicas sin ejecutar todas las demás
Uso: python3 test_multiples_fuentes.py --fuentes tdpi,ministerio_justicia,sii
"""

import argparse
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Agregar el directorio backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

def test_multiples_fuentes(fuentes: list, max_noticias: int = 3):
    """Probar múltiples fuentes específicas"""
    
    print(f"🧪 PROBANDO MÚLTIPLES FUENTES: {', '.join(fuentes).upper()}")
    print("=" * 80)
    
    resultados = {}
    
    for fuente in fuentes:
        print(f"\n🔍 PROBANDO: {fuente.upper()}")
        print("-" * 40)
        
        try:
            # Importar y ejecutar el scraper específico
            if fuente == 'tdpi':
                from backend.scrapers.fuentes.tdpi.tdpi_scraper import TDPScraper as TDPIScraper
                scraper = TDPIScraper(openai_api_key=os.getenv('OPENAI_API_KEY'))
            elif fuente == 'ministerio_justicia':
                from backend.scrapers.fuentes.ministerio_justicia.ministerio_justicia_scraper import MinisterioJusticiaScraper
                scraper = MinisterioJusticiaScraper(openai_api_key=os.getenv('OPENAI_API_KEY'))
            elif fuente == 'sii':
                from backend.scrapers.fuentes.sii.sii_scraper import SIIScraper
                scraper = SIIScraper(openai_api_key=os.getenv('OPENAI_API_KEY'))
            elif fuente == 'inapi':
                from backend.scrapers.fuentes.inapi.inapi_scraper import INAPIScraper
                scraper = INAPIScraper(openai_api_key=os.getenv('OPENAI_API_KEY'))
            elif fuente == 'contraloria':
                from backend.scrapers.fuentes.contraloria.contraloria_scraper import ContraloriaScraper
                scraper = ContraloriaScraper(openai_api_key=os.getenv('OPENAI_API_KEY'))
            elif fuente == 'tdlc':
                from backend.scrapers.fuentes.tdlc.tdlc_scraper import TDLScraper
                scraper = TDLScraper(openai_api_key=os.getenv('OPENAI_API_KEY'))
            elif fuente == '1ta':
                import importlib.util
                spec = importlib.util.spec_from_file_location("1ta_scraper", "backend/scrapers/fuentes/1ta/1ta_scraper.py")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                scraper = module.PrimerTribunalAmbientalScraper(openai_api_key=os.getenv('OPENAI_API_KEY'))
            else:
                # Importar desde el módulo principal
                from backend.scrapers.fuentes import (
                    PoderJudicialScraper, ContraloriaScraper, CDEScraper, TDLScraper,
                    PrimerTribunalAmbientalScraper, TercerTribunalAmbientalScraper,
                    TribunalAmbientalScraper, SIIScraper, TTAScraper, INAPIScraper, DTScraper
                )
                
                scraper_map = {
                    'poder_judicial': PoderJudicialScraper,
                    'cde': CDEScraper,
                    '3ta': TercerTribunalAmbientalScraper,
                    'tribunal_ambiental': TribunalAmbientalScraper,
                    'tta': TTAScraper,
                    'dt': DTScraper
                }
                
                if fuente not in scraper_map:
                    print(f"❌ Fuente '{fuente}' no soportada")
                    resultados[fuente] = {'estado': 'error', 'mensaje': 'Fuente no soportada'}
                    continue
                
                scraper = scraper_map[fuente](openai_api_key=os.getenv('OPENAI_API_KEY'))
            
            # Ejecutar scraping
            if hasattr(scraper, 'scrape_noticias_recientes'):
                noticias = scraper.scrape_noticias_recientes(max_noticias=max_noticias)
            elif hasattr(scraper, 'scrape'):
                noticias = scraper.scrape()
            else:
                print(f"❌ Método de scraping no encontrado")
                resultados[fuente] = {'estado': 'error', 'mensaje': 'Método no encontrado'}
                continue
            
            print(f"✅ Se extrajeron {len(noticias)} noticias")
            
            # Mostrar resumen
            for i, noticia in enumerate(noticias[:2], 1):  # Mostrar solo las primeras 2
                if hasattr(noticia, 'titulo'):
                    titulo = noticia.titulo
                else:
                    titulo = noticia.get('titulo', 'Sin título')
                
                print(f"  {i}. {titulo[:60]}...")
            
            if len(noticias) > 2:
                print(f"  ... y {len(noticias) - 2} noticias más")
            
            resultados[fuente] = {'estado': 'exito', 'noticias': len(noticias)}
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            resultados[fuente] = {'estado': 'error', 'mensaje': str(e)}
    
    # Resumen final
    print(f"\n📊 RESUMEN FINAL")
    print("=" * 80)
    
    exitosos = 0
    errores = 0
    
    for fuente, resultado in resultados.items():
        if resultado['estado'] == 'exito':
            print(f"✅ {fuente}: {resultado['noticias']} noticias extraídas")
            exitosos += 1
        else:
            print(f"❌ {fuente}: {resultado['mensaje']}")
            errores += 1
    
    print(f"\n🎯 RESULTADO: {exitosos} exitosos, {errores} errores")
    
    if exitosos == len(fuentes):
        print("🎉 ¡TODAS LAS FUENTES FUNCIONAN PERFECTAMENTE!")
    elif exitosos > 0:
        print("⚠️ Algunas fuentes funcionan, otras necesitan corrección")
    else:
        print("💥 Todas las fuentes tienen problemas")

def main():
    parser = argparse.ArgumentParser(description='Probar múltiples fuentes específicas')
    parser.add_argument('--fuentes', required=True, help='Fuentes a probar separadas por coma (ej: tdpi,ministerio_justicia,sii)')
    parser.add_argument('--max-noticias', type=int, default=3, help='Máximo número de noticias por fuente')
    
    args = parser.parse_args()
    
    fuentes = [f.strip() for f in args.fuentes.split(',')]
    test_multiples_fuentes(fuentes, args.max_noticias)

if __name__ == "__main__":
    main() 
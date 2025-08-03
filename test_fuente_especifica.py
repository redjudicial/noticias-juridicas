#!/usr/bin/env python3
"""
Script para probar una fuente específica sin ejecutar todas las demás
Uso: python3 test_fuente_especifica.py --fuente tdpi
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

def test_fuente_especifica(fuente_nombre: str, max_noticias: int = 5):
    """Probar una fuente específica"""
    
    print(f"🧪 PROBANDO FUENTE ESPECÍFICA: {fuente_nombre.upper()}")
    print("=" * 60)
    
    # Configuración de Supabase
    from supabase import create_client, Client
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Mapeo de fuentes a scrapers
    scrapers_config = {
        'poder_judicial': 'PoderJudicialScraper',
        'contraloria': 'ContraloriaScraper', 
        'cde': 'CDEScraper',
        'tdlc': 'TDLScraper',
        '1ta': 'PrimerTribunalAmbientalScraper',
        '3ta': 'TercerTribunalAmbientalScraper',
        'tribunal_ambiental': 'TribunalAmbientalScraper',
        'sii': 'SIIScraper',
        'tta': 'TTAScraper',
        'inapi': 'INAPIScraper',
        'dt': 'DTScraper',
        'tdpi': 'TDPIScraper',
        'ministerio_justicia': 'MinisterioJusticiaScraper'
    }
    
    if fuente_nombre not in scrapers_config:
        print(f"❌ Fuente '{fuente_nombre}' no encontrada")
        print(f"📋 Fuentes disponibles: {', '.join(scrapers_config.keys())}")
        return
    
    try:
        # Importar el scraper específico
        scraper_class_name = scrapers_config[fuente_nombre]
        
        if fuente_nombre == 'tdpi':
            from backend.scrapers.fuentes.tdpi.tdpi_scraper import TDPScraper as TDPIScraper
            scraper = TDPIScraper(openai_api_key=os.getenv('OPENAI_API_KEY'))
        elif fuente_nombre == 'ministerio_justicia':
            from backend.scrapers.fuentes.ministerio_justicia.ministerio_justicia_scraper import MinisterioJusticiaScraper
            scraper = MinisterioJusticiaScraper(openai_api_key=os.getenv('OPENAI_API_KEY'))
        else:
            # Importar desde el módulo principal
            from backend.scrapers.fuentes import (
                PoderJudicialScraper, ContraloriaScraper, CDEScraper, TDLScraper,
                PrimerTribunalAmbientalScraper, TercerTribunalAmbientalScraper,
                TribunalAmbientalScraper, SIIScraper, TTAScraper, INAPIScraper, DTScraper
            )
            scraper_class = globals()[scraper_class_name]
            scraper = scraper_class(openai_api_key=os.getenv('OPENAI_API_KEY'))
        
        print(f"🔍 Iniciando scraping de {fuente_nombre}...")
        
        # Ejecutar scraping
        if hasattr(scraper, 'scrape_noticias_recientes'):
            noticias = scraper.scrape_noticias_recientes(max_noticias=max_noticias)
        elif hasattr(scraper, 'scrape'):
            noticias = scraper.scrape()
        else:
            print(f"❌ Método de scraping no encontrado para {fuente_nombre}")
            return
        
        print(f"✅ Se extrajeron {len(noticias)} noticias de {fuente_nombre}")
        
        # Mostrar resumen de las noticias
        for i, noticia in enumerate(noticias[:3], 1):  # Mostrar solo las primeras 3
            if hasattr(noticia, 'titulo'):
                titulo = noticia.titulo
                fecha = noticia.fecha_publicacion
            else:
                titulo = noticia.get('titulo', 'Sin título')
                fecha = noticia.get('fecha_publicacion', 'Sin fecha')
            
            print(f"  {i}. {titulo[:80]}...")
            print(f"     📅 {fecha}")
        
        if len(noticias) > 3:
            print(f"  ... y {len(noticias) - 3} noticias más")
        
        print(f"\n✅ PRUEBA EXITOSA: {fuente_nombre} está funcionando correctamente")
        
    except Exception as e:
        print(f"❌ ERROR probando {fuente_nombre}: {e}")
        import traceback
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description='Probar una fuente específica')
    parser.add_argument('--fuente', required=True, help='Nombre de la fuente a probar')
    parser.add_argument('--max-noticias', type=int, default=5, help='Máximo número de noticias a extraer')
    
    args = parser.parse_args()
    
    test_fuente_especifica(args.fuente, args.max_noticias)

if __name__ == "__main__":
    main() 
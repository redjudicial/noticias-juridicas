#!/usr/bin/env python3
"""
Script para probar el scraper de Contraloría
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(__file__))

def test_contraloria_scraper():
    """Probar el scraper de Contraloría"""
    try:
        from backend.scrapers.fuentes.contraloria import ContraloriaScraper
        
        print("🧪 PROBANDO SCRAPER DE CONTRALORÍA")
        print("=" * 50)
        
        # Crear instancia del scraper
        scraper = ContraloriaScraper()
        
        # Probar obtención de enlaces
        print("🔍 Obteniendo enlaces de noticias...")
        enlaces = scraper.get_noticias_recientes(5)
        
        if enlaces:
            print(f"✅ Encontrados {len(enlaces)} enlaces:")
            for i, enlace in enumerate(enlaces, 1):
                print(f"   {i}. {enlace['titulo'][:60]}...")
                print(f"      URL: {enlace['url']}")
                print()
            
            # Probar extracción de una noticia completa
            if enlaces:
                print("📄 Extrayendo noticia completa...")
                noticia = scraper.get_noticia_completa(enlaces[0]['url'], enlaces[0]['titulo'])
                
                if noticia:
                    print("✅ Noticia extraída exitosamente:")
                    print(f"   Título: {noticia.titulo}")
                    print(f"   Fuente: {noticia.fuente_nombre_completo}")
                    print(f"   Fecha: {noticia.fecha_publicacion}")
                    print(f"   Categoría: {noticia.categoria}")
                    print(f"   Jurisdicción: {noticia.jurisdiccion}")
                    print(f"   Contenido: {len(noticia.cuerpo_completo)} caracteres")
                    print(f"   URL: {noticia.url_origen}")
                else:
                    print("❌ No se pudo extraer la noticia completa")
        else:
            print("❌ No se encontraron enlaces de noticias")
            
    except ImportError as e:
        print(f"❌ Error importando scraper de Contraloría: {e}")
    except Exception as e:
        print(f"❌ Error probando scraper de Contraloría: {e}")

def test_contraloria_scraping_completo():
    """Probar scraping completo de Contraloría"""
    try:
        from backend.scrapers.fuentes.contraloria import ContraloriaScraper
        
        print("\n🚀 PROBANDO SCRAPING COMPLETO DE CONTRALORÍA")
        print("=" * 50)
        
        scraper = ContraloriaScraper()
        noticias = scraper.scrape_noticias_recientes(3)
        
        if noticias:
            print(f"✅ Scraping completado: {len(noticias)} noticias extraídas")
            for i, noticia in enumerate(noticias, 1):
                print(f"\n📰 Noticia {i}:")
                print(f"   Título: {noticia.titulo}")
                print(f"   Fuente: {noticia.fuente_nombre_completo}")
                print(f"   Fecha: {noticia.fecha_publicacion}")
                print(f"   Categoría: {noticia.categoria}")
                print(f"   Jurisdicción: {noticia.jurisdiccion}")
                print(f"   Contenido: {len(noticia.cuerpo_completo)} caracteres")
        else:
            print("❌ No se extrajeron noticias")
            
    except Exception as e:
        print(f"❌ Error en scraping completo: {e}")

if __name__ == "__main__":
    test_contraloria_scraper()
    test_contraloria_scraping_completo() 
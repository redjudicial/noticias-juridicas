#!/usr/bin/env python3
"""
Script para ejecutar solo el scraper TTA y guardar en Supabase
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.main import NoticiasJuridicasSystem

def main():
    """Ejecutar solo TTA y guardar en Supabase"""
    print("🚀 EJECUTANDO SOLO SCRAPER TTA")
    print("=" * 50)
    
    try:
        # Inicializar sistema
        sistema = NoticiasJuridicasSystem()
        
        # Ejecutar solo TTA
        print("🔍 Scrapeando noticias de TTA...")
        
        # Obtener scraper TTA
        tta_scraper = sistema.scrapers.get('tta')
        if not tta_scraper:
            print("❌ Scraper TTA no encontrado")
            return
        
        # Obtener noticias
        noticias = tta_scraper.scrape_noticias_recientes(max_noticias=5)
        
        if noticias:
            print(f"✅ Encontradas {len(noticias)} noticias de TTA")
            
            # Guardar en Supabase
            print("💾 Guardando en Supabase...")
            exitosas = 0
            
            for noticia in noticias:
                try:
                    resultado = sistema.supabase.table('noticias_limpias').insert({
                        'titulo': noticia.titulo,
                        'cuerpo_completo': noticia.cuerpo_completo,
                        'fecha_publicacion': noticia.fecha_publicacion.isoformat(),
                        'fuente': noticia.fuente,
                        'url_origen': noticia.url_origen,
                        'categoria': noticia.categoria.value if hasattr(noticia.categoria, 'value') else str(noticia.categoria),
                        'jurisdiccion': noticia.jurisdiccion.value if hasattr(noticia.jurisdiccion, 'value') else str(noticia.jurisdiccion),
                        'tipo_documento': noticia.tipo_documento.value if hasattr(noticia.tipo_documento, 'value') else str(noticia.tipo_documento),
                        'fuente_nombre_completo': noticia.fuente_nombre_completo,
                        'tribunal_organismo': noticia.tribunal_organismo
                    }).execute()
                    
                    if resultado.data:
                        exitosas += 1
                        print(f"✅ Guardada: {noticia.titulo[:50]}...")
                    
                except Exception as e:
                    if "duplicate key" in str(e).lower():
                        print(f"ℹ️ Ya existe: {noticia.titulo[:50]}...")
                    else:
                        print(f"❌ Error guardando: {str(e)}")
            
            print(f"\n🎯 RESULTADO: {exitosas} noticias nuevas de TTA guardadas")
            
        else:
            print("❌ No se encontraron noticias de TTA")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
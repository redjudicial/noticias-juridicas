#!/usr/bin/env python3
"""
Script de prueba específico para Contraloría y CDE
Solo prueba estos dos scrapers que tienen problemas
"""

import sys
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.scrapers.fuentes.contraloria.contraloria_scraper import ContraloriaScraper
from backend.scrapers.fuentes.cde.cde_scraper import CDEScraper
from backend.database.supabase_client import SupabaseClient

def test_contraloria_cde():
    """Probar solo Contraloría y CDE"""
    print("🧪 **PRUEBA ESPECÍFICA: CONTRALORÍA Y CDE**")
    print("=" * 50)
    
    # Inicializar Supabase con credenciales
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Error: Faltan credenciales de Supabase")
        print(f"URL: {supabase_url}")
        print(f"KEY: {'SÍ' if supabase_key else 'NO'}")
        return
    
    supabase = SupabaseClient(supabase_url, supabase_key)
    
    # Probar Contraloría
    print("\n📰 **PROBANDO CONTRALORÍA**")
    print("-" * 30)
    
    try:
        contraloria = ContraloriaScraper()
        noticias_contraloria = contraloria.scrape_noticias_recientes(max_noticias=2)
        
        if noticias_contraloria:
            print(f"✅ Contraloría: {len(noticias_contraloria)} noticias extraídas")
            for i, noticia in enumerate(noticias_contraloria, 1):
                print(f"  {i}. {noticia.titulo[:60]}...")
                
                # Intentar guardar en Supabase
                try:
                    resultado = supabase.insert_noticia(noticia)
                    if resultado:
                        print(f"    ✅ Guardada en Supabase")
                    else:
                        print(f"    ❌ Error guardando en Supabase")
                except Exception as e:
                    print(f"    ❌ Error Supabase: {e}")
        else:
            print("❌ Contraloría: No se extrajeron noticias")
            
    except Exception as e:
        print(f"❌ Error en Contraloría: {e}")
    
    # Probar CDE
    print("\n📰 **PROBANDO CDE**")
    print("-" * 30)
    
    try:
        cde = CDEScraper()
        noticias_cde = cde.scrape_noticias_recientes(max_noticias=2)
        
        if noticias_cde:
            print(f"✅ CDE: {len(noticias_cde)} noticias extraídas")
            for i, noticia in enumerate(noticias_cde, 1):
                print(f"  {i}. {noticia.titulo[:60]}...")
                
                # Intentar guardar en Supabase
                try:
                    resultado = supabase.insert_noticia(noticia)
                    if resultado:
                        print(f"    ✅ Guardada en Supabase")
                    else:
                        print(f"    ❌ Error guardando en Supabase")
                except Exception as e:
                    print(f"    ❌ Error Supabase: {e}")
        else:
            print("❌ CDE: No se extrajeron noticias")
            
    except Exception as e:
        print(f"❌ Error en CDE: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 **PRUEBA COMPLETADA**")

if __name__ == "__main__":
    test_contraloria_cde() 
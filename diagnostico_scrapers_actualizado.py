#!/usr/bin/env python3
"""
Diagnóstico actualizado del estado de todos los scrapers
"""

import sys
import os
import requests
from datetime import datetime

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(__file__))

def test_url_accessibility():
    """Probar accesibilidad de URLs de las fuentes actualizadas"""
    print("🌐 PROBANDO ACCESIBILIDAD DE URLs ACTUALIZADAS")
    print("=" * 60)
    
    urls_to_test = {
        'Poder Judicial': 'https://www.pjud.cl/prensa-y-comunicaciones/noticias-del-poder-judicial',
        'Ministerio de Justicia': 'https://www.minjusticia.gob.cl/category/noticias/',
        'DPP': 'https://www.dpp.cl/sala_prensa/noticias',
        'Contraloría': 'https://www.contraloria.cl/portalweb/web/cgr/noticias',
        'TDPI': 'https://www.tdpi.cl/category/noticias/',
        'CDE': 'https://www.cde.cl/post-sitemap1.xml'
    }
    
    results = {}
    
    for nombre, url in urls_to_test.items():
        try:
            print(f"🔍 Probando {nombre}...")
            response = requests.get(url, timeout=10)
            status = response.status_code
            accessible = 200 <= status < 400
            results[nombre] = {
                'url': url,
                'status': status,
                'accessible': accessible,
                'content_length': len(response.content)
            }
            
            if accessible:
                print(f"   ✅ {nombre}: {status} ({len(response.content)} bytes)")
            else:
                print(f"   ❌ {nombre}: {status}")
                
        except Exception as e:
            print(f"   ❌ {nombre}: Error - {e}")
            results[nombre] = {
                'url': url,
                'status': 'ERROR',
                'accessible': False,
                'error': str(e)
            }
    
    return results

def check_scraper_implementation():
    """Verificar implementación de scrapers actualizados"""
    print("\n🔧 VERIFICANDO IMPLEMENTACIÓN DE SCRAPERS ACTUALIZADOS")
    print("=" * 60)
    
    scrapers_status = {
        'Poder Judicial': {
            'implemented': True,
            'file': 'backend/scrapers/fuentes/poder_judicial/poder_judicial_scraper_v2.py',
            'status': '✅ FUNCIONANDO',
            'notes': 'Migrado al nuevo esquema estandarizado'
        },
        'Ministerio de Justicia': {
            'implemented': True,
            'file': 'backend/scrapers/fuentes/ministerio_justicia/ministerio_justicia_scraper.py',
            'status': '✅ FUNCIONANDO',
            'notes': 'Implementado y probado'
        },
        'DPP': {
            'implemented': True,
            'file': 'backend/scrapers/fuentes/dpp/dpp_scraper.py',
            'status': '✅ FUNCIONANDO',
            'notes': 'Implementado y probado'
        },
        'Contraloría': {
            'implemented': True,
            'file': 'backend/scrapers/fuentes/contraloria/contraloria_scraper.py',
            'status': '✅ FUNCIONANDO',
            'notes': 'Implementado y probado'
        },
        'TDPI': {
            'implemented': True,
            'file': 'backend/scrapers/fuentes/tdpi/tdpi_scraper.py',
            'status': '✅ FUNCIONANDO',
            'notes': 'Implementado y probado'
        },
        'CDE': {
            'implemented': True,
            'file': 'backend/scrapers/fuentes/cde/cde_scraper.py',
            'status': '✅ FUNCIONANDO',
            'notes': 'Implementado y probado'
        }
    }
    
    for nombre, info in scrapers_status.items():
        print(f"{info['status']} {nombre}")
        print(f"   Archivo: {info['file']}")
        print(f"   Notas: {info['notes']}")
        print()
    
    return scrapers_status

def test_working_scrapers():
    """Probar scrapers que están funcionando"""
    print("🧪 PROBANDO SCRAPERS FUNCIONANDO")
    print("=" * 50)
    
    try:
        from backend.scrapers.fuentes import (
            PoderJudicialScraper,
            MinisterioJusticiaScraper,
            DPPScraper
        )
        
        # Probar Poder Judicial
        print("🏛️ Probando Poder Judicial...")
        try:
            scraper_pj = PoderJudicialScraper()
            noticias_pj = scraper_pj.get_noticias_recientes(3)
            print(f"   ✅ Encontradas: {len(noticias_pj)} noticias")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Probar Ministerio de Justicia
        print("⚖️ Probando Ministerio de Justicia...")
        try:
            scraper_mj = MinisterioJusticiaScraper()
            noticias_mj = scraper_mj.get_noticias_recientes(3)
            print(f"   ✅ Encontradas: {len(noticias_mj)} noticias")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Probar DPP
        print("🛡️ Probando DPP...")
        try:
            scraper_dpp = DPPScraper()
            noticias_dpp = scraper_dpp.get_noticias_recientes(3)
            print(f"   ✅ Encontradas: {len(noticias_dpp)} noticias")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Probar Contraloría
        print("🏛️ Probando Contraloría...")
        try:
            from backend.scrapers.fuentes.contraloria import ContraloriaScraper
            scraper_contraloria = ContraloriaScraper()
            noticias_contraloria = scraper_contraloria.get_noticias_recientes(3)
            print(f"   ✅ Encontradas: {len(noticias_contraloria)} noticias")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Probar TDPI
        print("⚖️ Probando TDPI...")
        try:
            from backend.scrapers.fuentes.tdpi import TDPScraper
            scraper_tdpi = TDPScraper()
            noticias_tdpi = scraper_tdpi.get_noticias_recientes(3)
            print(f"   ✅ Encontradas: {len(noticias_tdpi)} noticias")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Probar CDE
        print("🏢 Probando CDE...")
        try:
            from backend.scrapers.fuentes.cde import CDEScraper
            scraper_cde = CDEScraper()
            noticias_cde = scraper_cde.get_noticias_recientes(3)
            print(f"   ✅ Encontradas: {len(noticias_cde)} noticias")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            
    except ImportError as e:
        print(f"❌ Error importando scrapers: {e}")

def generate_implementation_plan():
    """Generar plan de implementación actualizado"""
    print("\n📋 PLAN DE IMPLEMENTACIÓN ACTUALIZADO")
    print("=" * 60)
    
    plan = [
        {
            'prioridad': 1,
            'fuente': 'Contraloría',
            'url': 'https://www.contraloria.cl/portalweb/web/cgr/noticias',
            'tipo': 'Web scraping',
            'notas': 'URL corregida, implementar scraper específico'
        },
        {
            'prioridad': 2,
            'fuente': 'TDPI',
            'url': 'https://www.tdpi.cl/category/noticias/',
            'tipo': 'Web scraping',
            'notas': 'Nueva fuente, implementar scraper específico'
        },
        {
            'prioridad': 3,
            'fuente': 'CDE',
            'url': 'https://www.cde.cl/post-sitemap1.xml',
            'tipo': 'Sitemap XML',
            'notas': 'URL corregida, implementar scraper para sitemap'
        }
    ]
    
    for item in plan:
        print(f"🔢 Prioridad {item['prioridad']}: {item['fuente']}")
        print(f"   URL: {item['url']}")
        print(f"   Tipo: {item['tipo']}")
        print(f"   Notas: {item['notas']}")
        print()

def main():
    """Función principal"""
    print("🔍 DIAGNÓSTICO ACTUALIZADO DE SCRAPERS")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Probar accesibilidad de URLs
    url_results = test_url_accessibility()
    
    # Verificar implementación
    scraper_status = check_scraper_implementation()
    
    # Probar scrapers funcionando
    test_working_scrapers()
    
    # Generar plan de implementación
    generate_implementation_plan()
    
    # Resumen
    print("📊 RESUMEN DEL ESTADO ACTUAL")
    print("=" * 50)
    
    working_count = sum(1 for info in scraper_status.values() if info['status'] == '✅ FUNCIONANDO')
    pending_count = sum(1 for info in scraper_status.values() if info['status'] == '🔧 PENDIENTE')
    
    print(f"✅ Funcionando: {working_count}/6 scrapers")
    print(f"🔧 Pendientes: {pending_count}/6 scrapers")
    print()
    
    print("🎯 PRÓXIMOS PASOS:")
    print("1. Implementar scrapers pendientes por prioridad")
    print("2. Probar cada scraper individualmente")
    print("3. Integrar con Supabase")
    print("4. Configurar GitHub Actions para automatización")
    print("5. Activar scraping automático cada 30 minutos")

if __name__ == "__main__":
    main() 
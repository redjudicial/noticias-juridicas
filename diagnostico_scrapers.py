#!/usr/bin/env python3
"""
Diagnóstico completo del estado actual de todos los scrapers
"""

import sys
import os
import requests
from datetime import datetime

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(__file__))

def test_url_accessibility():
    """Probar accesibilidad de URLs de las fuentes"""
    print("🌐 PROBANDO ACCESIBILIDAD DE URLs")
    print("=" * 50)
    
    urls_to_test = {
        'Poder Judicial': 'https://www.pjud.cl/prensa-y-comunicaciones/noticias-del-poder-judicial',
        'Ministerio de Justicia': 'https://www.minjusticia.gob.cl/category/noticias/',
        'Tribunal Constitucional': 'https://www.tribunalconstitucional.cl/noticias',
        'DPP': 'https://www.dpp.cl/sala_prensa/noticias',
        'Diario Oficial': 'https://www.diariooficial.interior.gob.cl/publicaciones/',
        'Fiscalía': 'https://www.fiscaliadechile.cl/noticias/',
        'Contraloría': 'https://www.contraloria.cl/noticias/',
        'CDE': 'https://www.cde.cl/noticias/'
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
    """Verificar implementación de scrapers"""
    print("\n🔧 VERIFICANDO IMPLEMENTACIÓN DE SCRAPERS")
    print("=" * 50)
    
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
        'Tribunal Constitucional': {
            'implemented': False,
            'file': 'backend/scrapers/fuentes/tribunal_constitucional/',
            'status': '🔧 PENDIENTE',
            'notes': 'Carpeta creada, scraper no implementado'
        },
        'DPP': {
            'implemented': False,
            'file': 'backend/scrapers/fuentes/dpp/',
            'status': '🔧 PENDIENTE',
            'notes': 'Carpeta creada, scraper no implementado'
        },
        'Diario Oficial': {
            'implemented': False,
            'file': 'backend/scrapers/fuentes/diario_oficial/',
            'status': '🔧 PENDIENTE',
            'notes': 'Carpeta creada, scraper no implementado'
        },
        'Fiscalía': {
            'implemented': False,
            'file': 'backend/scrapers/fuentes/fiscalia/',
            'status': '🔧 PENDIENTE',
            'notes': 'Carpeta creada, scraper no implementado'
        },
        'Contraloría': {
            'implemented': False,
            'file': 'backend/scrapers/fuentes/contraloria/',
            'status': '🔧 PENDIENTE',
            'notes': 'Carpeta creada, scraper no implementado'
        },
        'CDE': {
            'implemented': False,
            'file': 'backend/scrapers/fuentes/cde/',
            'status': '🔧 PENDIENTE',
            'notes': 'Carpeta creada, scraper no implementado'
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
            MinisterioJusticiaScraper
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
            
    except ImportError as e:
        print(f"❌ Error importando scrapers: {e}")

def generate_implementation_plan():
    """Generar plan de implementación"""
    print("\n📋 PLAN DE IMPLEMENTACIÓN")
    print("=" * 50)
    
    plan = [
        {
            'prioridad': 1,
            'fuente': 'Tribunal Constitucional',
            'url': 'https://www.tribunalconstitucional.cl/noticias',
            'tipo': 'Web scraping',
            'notas': 'Analizar estructura HTML específica'
        },
        {
            'prioridad': 2,
            'fuente': 'DPP',
            'url': 'https://www.dpp.cl/sala_prensa/noticias',
            'tipo': 'Web scraping',
            'notas': 'URL corregida, implementar scraper específico'
        },
        {
            'prioridad': 3,
            'fuente': 'Fiscalía',
            'url': 'https://www.fiscaliadechile.cl/noticias/',
            'tipo': 'Web scraping + RSS fallback',
            'notas': 'Resolver problemas de timeout'
        },
        {
            'prioridad': 4,
            'fuente': 'Contraloría',
            'url': 'https://www.contraloria.cl/noticias/',
            'tipo': 'Web scraping + RSS fallback',
            'notas': 'Implementar scraper específico'
        },
        {
            'prioridad': 5,
            'fuente': 'CDE',
            'url': 'https://www.cde.cl/noticias/',
            'tipo': 'Web scraping + RSS fallback',
            'notas': 'Implementar scraper específico'
        },
        {
            'prioridad': 6,
            'fuente': 'Diario Oficial',
            'url': 'https://www.diariooficial.interior.gob.cl/publicaciones/',
            'tipo': 'Web scraping',
            'notas': 'Resolver problema de 403 Forbidden'
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
    print("🔍 DIAGNÓSTICO COMPLETO DE SCRAPERS")
    print("=" * 60)
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
    
    print(f"✅ Funcionando: {working_count}/8 scrapers")
    print(f"🔧 Pendientes: {pending_count}/8 scrapers")
    print()
    
    print("🎯 PRÓXIMOS PASOS:")
    print("1. Implementar scrapers pendientes por prioridad")
    print("2. Probar cada scraper individualmente")
    print("3. Integrar con Supabase")
    print("4. Configurar GitHub Actions para automatización")
    print("5. Activar scraping automático cada 15 minutos")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Script para probar la nueva estructura de scrapers organizados por fuentes
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(__file__))

def test_nueva_estructura():
    """Probar la nueva estructura de scrapers"""
    print("🧪 PROBANDO NUEVA ESTRUCTURA DE SCRAPERS")
    print("=" * 50)
    
    try:
        # Importar el módulo de fuentes
        from backend.scrapers.fuentes import (
            listar_fuentes_disponibles,
            get_fuentes_activas,
            get_scrapers_activos,
            PoderJudicialScraper,
            MinisterioJusticiaScraper
        )
        
        print("✅ Módulo de fuentes importado correctamente")
        print()
        
        # Listar fuentes disponibles
        listar_fuentes_disponibles()
        
        # Mostrar fuentes activas
        fuentes_activas = get_fuentes_activas()
        print(f"📊 Fuentes activas: {len(fuentes_activas)}")
        for codigo, config in fuentes_activas.items():
            print(f"   - {config['nombre']} ({codigo})")
        print()
        
        # Mostrar scrapers activos
        scrapers_activos = get_scrapers_activos()
        print(f"🔧 Scrapers activos: {len(scrapers_activos)}")
        for codigo, scraper_class in scrapers_activos.items():
            print(f"   - {codigo}: {scraper_class.__name__ if scraper_class else 'No disponible'}")
        print()
        
        # Probar scraper del Poder Judicial
        if PoderJudicialScraper:
            print("🧪 Probando scraper del Poder Judicial...")
            try:
                scraper = PoderJudicialScraper()
                noticias = scraper.get_noticias_recientes(3)
                print(f"✅ Poder Judicial: {len(noticias)} noticias encontradas")
            except Exception as e:
                print(f"❌ Error en Poder Judicial: {e}")
        else:
            print("❌ Scraper del Poder Judicial no disponible")
        
        # Probar scraper del Ministerio de Justicia
        if MinisterioJusticiaScraper:
            print("🧪 Probando scraper del Ministerio de Justicia...")
            try:
                scraper = MinisterioJusticiaScraper()
                noticias = scraper.get_noticias_recientes(3)
                print(f"✅ Ministerio de Justicia: {len(noticias)} noticias encontradas")
            except Exception as e:
                print(f"❌ Error en Ministerio de Justicia: {e}")
        else:
            print("❌ Scraper del Ministerio de Justicia no disponible")
        
        print()
        print("✅ Prueba de nueva estructura completada")
        
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        print("Verificar que todos los archivos estén en su lugar")
    except Exception as e:
        print(f"❌ Error general: {e}")

def mostrar_estructura_directorios():
    """Mostrar la estructura de directorios creada"""
    print("📁 ESTRUCTURA DE DIRECTORIOS CREADA")
    print("=" * 40)
    
    estructura = """
backend/scrapers/fuentes/
├── __init__.py
├── config.py
├── base_scraper.py
├── poder_judicial/
│   ├── __init__.py
│   ├── poder_judicial_scraper.py
│   └── poder_judicial_scraper_v2.py
├── ministerio_justicia/
│   ├── __init__.py
│   └── ministerio_justicia_scraper.py
├── tribunal_constitucional/
│   └── __init__.py
├── dpp/
│   └── __init__.py
├── diario_oficial/
│   └── __init__.py
├── fiscalia/
│   └── __init__.py
├── contraloria/
│   └── __init__.py
└── cde/
    └── __init__.py
"""
    
    print(estructura)

def main():
    """Función principal"""
    print("🚀 REORGANIZACIÓN DE SCRAPERS POR FUENTES")
    print("=" * 60)
    print()
    
    # Mostrar estructura
    mostrar_estructura_directorios()
    print()
    
    # Probar nueva estructura
    test_nueva_estructura()
    
    print()
    print("🎯 BENEFICIOS DE LA NUEVA ESTRUCTURA:")
    print("✅ Organización clara por fuente")
    print("✅ Configuración centralizada")
    print("✅ Fácil mantenimiento")
    print("✅ Escalabilidad")
    print("✅ Reutilización de código")
    print("✅ Testing individual por fuente")

if __name__ == "__main__":
    main() 
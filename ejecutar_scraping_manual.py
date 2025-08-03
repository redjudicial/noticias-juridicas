#!/usr/bin/env python3
"""
Script para ejecutar scraping manual de todos los scrapers
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
    """Ejecutar scraping manual"""
    print("🚀 EJECUTANDO SCRAPING MANUAL")
    print("=" * 50)
    
    try:
        # Inicializar sistema
        sistema = NoticiasJuridicasSystem()
        
        # Ejecutar scraping
        print("🔍 Iniciando scraping de todas las fuentes...")
        resultado = sistema.ejecutar_scraping()
        
        print(f"\n🎯 SCRAPING COMPLETADO")
        print(f"📊 Resultado: {resultado}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

 
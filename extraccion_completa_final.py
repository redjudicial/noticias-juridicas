#!/usr/bin/env python3
"""
Extracción completa de noticias desde el 21 de julio de 2025
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Agregar el directorio backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from main import SistemaNoticiasJuridicas

def extraccion_completa():
    """Ejecutar extracción completa desde el 21 de julio"""
    
    print("🚀 **EXTRACCIÓN COMPLETA DE NOTICIAS**")
    print("=" * 50)
    print(f"📅 Desde: 21 de julio de 2025")
    print(f"📅 Hasta: {datetime.now().strftime('%d de %B de %Y')}")
    print("=" * 50)
    
    # Cargar variables de entorno
    load_dotenv('APIS_Y_CREDENCIALES.env')
    
    # Inicializar sistema
    sistema = SistemaNoticiasJuridicas()
    
    # Configurar para extracción completa
    sistema.max_noticias_por_fuente = 100  # Más noticias por fuente
    sistema.fecha_inicio = datetime(2025, 7, 21)  # Desde el 21 de julio
    
    # Ejecutar scraping completo
    try:
        sistema.ejecutar_scraping_completo()
        print("
✅ **EXTRACCIÓN COMPLETADA EXITOSAMENTE**")
        print("🎯 Sistema listo para producción con GitHub Actions")
        
    except Exception as e:
        print(f"
❌ Error en extracción: {e}")
        sys.exit(1)

if __name__ == "__main__":
    extraccion_completa()

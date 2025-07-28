#!/usr/bin/env python3
"""
Script para verificar datos en Supabase
"""

import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

def verificar_datos():
    """Verificar datos en Supabase"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}'
    }
    
    print("🔍 **VERIFICACIÓN DE DATOS EN SUPABASE**")
    print("=" * 50)
    
    # Obtener noticias recientes
    try:
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&order=fecha_publicacion.desc&limit=5',
            headers=headers
        )
        
        if response.status_code == 200:
            noticias = response.json()
            
            print(f"📊 Total noticias recientes: {len(noticias)}")
            print("\n📰 **MUESTRA DE NOTICIAS:**")
            print("-" * 40)
            
            for i, noticia in enumerate(noticias, 1):
                print(f"\n{i}. **{noticia.get('titulo', 'Sin título')[:60]}...**")
                print(f"   📅 Fecha: {noticia.get('fecha_publicacion', 'N/A')}")
                print(f"   📰 Fuente: {noticia.get('fuente', 'N/A')}")
                print(f"   📝 Resumen: {noticia.get('resumen_ejecutivo', 'Sin resumen')[:80]}...")
                print(f"   🏷️  Palabras clave: {noticia.get('palabras_clave', [])}")
                print(f"   🔗 URL: {noticia.get('url_origen', 'N/A')[:50]}...")
                
        else:
            print(f"❌ Error obteniendo noticias: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Obtener estadísticas
    try:
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=count',
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                total = result[0]['count']
                print(f"\n📈 **ESTADÍSTICAS:**")
                print(f"   • Total noticias: {total}")
                
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")

if __name__ == "__main__":
    verificar_datos() 
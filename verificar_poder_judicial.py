#!/usr/bin/env python3
"""
Verificar noticias del Poder Judicial específicamente
"""

import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

def verificar_poder_judicial():
    """Verificar noticias del Poder Judicial"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}'
    }
    
    print("🔍 **VERIFICACIÓN PODER JUDICIAL**")
    print("=" * 50)
    
    try:
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&fuente=eq.poder_judicial&order=fecha_publicacion.desc&limit=10',
            headers=headers
        )
        
        if response.status_code == 200:
            noticias = response.json()
            
            print(f"📊 Total noticias Poder Judicial: {len(noticias)}")
            print("\n📰 **NOTICIAS DEL PODER JUDICIAL:**")
            print("-" * 40)
            
            for i, noticia in enumerate(noticias, 1):
                print(f"\n{i}. **{noticia.get('titulo', 'Sin título')}**")
                print(f"   📅 Fecha publicación: {noticia.get('fecha_publicacion', 'N/A')}")
                print(f"   📅 Fecha actualización: {noticia.get('fecha_actualizacion', 'N/A')}")
                print(f"   📝 Resumen: {noticia.get('resumen_ejecutivo', 'Sin resumen')[:80]}...")
                print(f"   🔗 URL: {noticia.get('url_origen', 'N/A')[:50]}...")
                
                # Verificar si el título tiene fechas
                titulo = noticia.get('titulo', '')
                if any(char.isdigit() for char in titulo[-15:]):
                    print(f"   ⚠️  TÍTULO CON FECHA: {titulo[-20:]}")
                else:
                    print(f"   ✅ Título limpio")
                
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verificar_poder_judicial() 
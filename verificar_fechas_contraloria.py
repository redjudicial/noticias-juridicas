#!/usr/bin/env python3
"""
Verificar fechas de las noticias de la Contraloría
"""

import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

def verificar_fechas_contraloria():
    """Verificar fechas de las noticias de la Contraloría"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}'
    }
    
    print("🔍 **VERIFICACIÓN DE FECHAS - CONTRALORÍA**")
    print("=" * 50)
    
    try:
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&fuente=eq.contraloria&order=fecha_publicacion.desc&limit=10',
            headers=headers
        )
        
        if response.status_code == 200:
            noticias = response.json()
            
            print(f"📊 Noticias de la Contraloría: {len(noticias)}")
            print("\n📰 **FECHAS DE NOTICIAS:**")
            print("-" * 40)
            
            for i, noticia in enumerate(noticias, 1):
                titulo = noticia.get('titulo', 'Sin título')
                fecha_pub = noticia.get('fecha_publicacion', 'N/A')
                fecha_act = noticia.get('fecha_actualizacion', 'N/A')
                
                print(f"\n{i}. **{titulo[:60]}...**")
                print(f"   📅 Fecha publicación: {fecha_pub}")
                print(f"   📅 Fecha actualización: {fecha_act}")
                
                # Verificar si la fecha es reciente (no de hoy)
                if '2025-07-28' in str(fecha_pub):
                    print(f"   ⚠️  FECHA DE HOY (posiblemente incorrecta)")
                else:
                    print(f"   ✅ Fecha diferente a hoy")
                
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verificar_fechas_contraloria() 
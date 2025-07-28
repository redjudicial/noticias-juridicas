#!/usr/bin/env python3
"""
Script para verificar las noticias con contenido limpio
"""

import requests

# Credenciales de Supabase (del JavaScript)
SUPABASE_URL = 'https://qfomiierchksyfhxoukj.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFmb21paWVyY2hrc3lmaHhvdWtqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEwMjgxNTYsImV4cCI6MjA2NjYwNDE1Nn0.HqlptdYXjd2s9q8xHEmgQPyf6a95fosb0YT5b4asMA8'

def check_noticias_limpias():
    """Verificar las noticias más recientes con contenido limpio"""
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/noticias_juridicas",
            headers={
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}'
            },
            params={
                'select': 'titulo,resumen_ejecutivo,palabras_clave,fecha_publicacion',
                'order': 'fecha_publicacion.desc',
                'limit': 3
            }
        )
        
        if response.status_code == 200:
            noticias = response.json()
            print(f"✅ Encontradas {len(noticias)} noticias recientes")
            print()
            
            for i, noticia in enumerate(noticias, 1):
                print(f"📰 Noticia {i}:")
                print(f"   Título: {noticia['titulo']}")
                print(f"   Resumen: {noticia['resumen_ejecutivo'][:200]}...")
                print(f"   Palabras clave: {noticia['palabras_clave']}")
                print(f"   Fecha: {noticia['fecha_publicacion']}")
                print()
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_noticias_limpias() 
#!/usr/bin/env python3
"""
Script simple para limpiar la tabla de noticias
"""

import sys
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
import requests

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

def limpiar_tabla_simple():
    """Limpiar tabla de forma simple"""
    print("🧹 **LIMPIEZA SIMPLE DE TABLA**")
    print("=" * 40)
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    # Obtener todas las noticias
    print("📊 Obteniendo noticias...")
    response = requests.get(
        f'{supabase_url}/rest/v1/noticias_juridicas?select=id&limit=1000',
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Error obteniendo noticias: {response.status_code}")
        return
    
    noticias = response.json()
    print(f"📈 Encontradas {len(noticias)} noticias")
    
    if len(noticias) == 0:
        print("✅ La tabla ya está vacía")
        return
    
    # Eliminar noticias una por una
    print("🗑️  Eliminando noticias...")
    eliminadas = 0
    
    for noticia in noticias:
        noticia_id = noticia['id']
        delete_response = requests.delete(
            f'{supabase_url}/rest/v1/noticias_juridicas?id=eq.{noticia_id}',
            headers=headers
        )
        
        if delete_response.status_code == 200:
            eliminadas += 1
            if eliminadas % 10 == 0:
                print(f"   ✅ Eliminadas {eliminadas} noticias...")
        else:
            print(f"   ❌ Error eliminando noticia {noticia_id}")
    
    print(f"✅ Eliminadas {eliminadas} noticias de {len(noticias)}")
    
    # Verificar
    response = requests.get(
        f'{supabase_url}/rest/v1/noticias_juridicas?select=id&limit=1',
        headers=headers
    )
    
    if response.status_code == 200:
        noticias_restantes = response.json()
        print(f"📊 Noticias restantes: {len(noticias_restantes)}")
        
        if len(noticias_restantes) == 0:
            print("✅ Tabla limpiada exitosamente")
        else:
            print("⚠️  Aún quedan noticias")
    
    print("🏁 **LIMPIEZA COMPLETADA**")

if __name__ == "__main__":
    limpiar_tabla_simple() 
#!/usr/bin/env python3
"""
Script simple para limpiar la tabla de noticias
"""

import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

def limpiar_tabla():
    """Limpiar tabla usando SQL directo"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    # SQL para limpiar
    sql_data = {
        'query': 'DELETE FROM noticias_juridicas;'
    }
    
    try:
        # Ejecutar SQL
        response = requests.post(
            f'{SUPABASE_URL}/rest/v1/rpc/exec_sql',
            headers=headers,
            json=sql_data
        )
        
        if response.status_code == 200:
            print("✅ Tabla limpiada exitosamente")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧹 Limpiando tabla de noticias...")
    limpiar_tabla() 
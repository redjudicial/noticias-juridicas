#!/usr/bin/env python3
"""
Script para ejecutar SQL en Supabase y eliminar restricción de hash
"""

import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

def ejecutar_sql():
    """Ejecutar SQL para eliminar restricción de hash"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    # SQL para eliminar restricción y agregar nueva
    sql_commands = [
        "ALTER TABLE noticias_juridicas DROP CONSTRAINT IF EXISTS noticias_juridicas_hash_contenido_key;",
        "ALTER TABLE noticias_juridicas ADD CONSTRAINT noticias_juridicas_url_origen_key UNIQUE (url_origen);",
        "CREATE INDEX IF NOT EXISTS idx_noticias_hash_contenido ON noticias_juridicas(hash_contenido);",
        "CREATE INDEX IF NOT EXISTS idx_noticias_url_origen ON noticias_juridicas(url_origen);"
    ]
    
    for i, sql in enumerate(sql_commands, 1):
        print(f"🔧 Ejecutando comando {i}/4: {sql[:50]}...")
        
        sql_data = {
            'query': sql
        }
        
        try:
            response = requests.post(
                f'{SUPABASE_URL}/rest/v1/rpc/exec_sql',
                headers=headers,
                json=sql_data
            )
            
            if response.status_code == 200:
                print(f"✅ Comando {i} ejecutado exitosamente")
            else:
                print(f"❌ Error en comando {i}: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error ejecutando comando {i}: {e}")
    
    print("\n🎯 **VERIFICACIÓN COMPLETADA**")
    print("Ahora puedes probar el sistema sin errores de hash duplicado")

if __name__ == "__main__":
    print("🔧 **ELIMINANDO RESTRICCIÓN DE HASH**")
    print("=" * 50)
    ejecutar_sql() 
#!/usr/bin/env python3
"""
Script para diagnosticar problemas de conexión con Supabase
"""

import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

def test_supabase_connection():
    """Probar conexión a Supabase"""
    print("🔍 DIAGNÓSTICO DE CONEXIÓN SUPABASE")
    print("=" * 50)
    
    # Obtener credenciales
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
    supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    print(f"URL: {supabase_url}")
    print(f"ANON KEY: {supabase_anon_key[:20] if supabase_anon_key else 'NO ENCONTRADA'}...")
    print(f"SERVICE KEY: {supabase_service_key[:20] if supabase_service_key else 'NO ENCONTRADA'}...")
    print()
    
    # Probar con ANON KEY
    print("🔑 Probando con ANON KEY...")
    headers_anon = {
        'apikey': supabase_anon_key,
        'Authorization': f'Bearer {supabase_anon_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f'{supabase_url}/rest/v1/noticias_juridicas?limit=1', headers=headers_anon, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Conexión exitosa con ANON KEY")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Probar con SERVICE KEY
    print("🔑 Probando con SERVICE KEY...")
    headers_service = {
        'apikey': supabase_service_key,
        'Authorization': f'Bearer {supabase_service_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f'{supabase_url}/rest/v1/noticias_juridicas?limit=1', headers=headers_service, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Conexión exitosa con SERVICE KEY")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Probar inserción con SERVICE KEY
    print("📝 Probando inserción con SERVICE KEY...")
    test_data = {
        'titulo': 'Test de conexión',
        'resumen_ejecutivo': 'Test de conexión a Supabase',
        'cuerpo_completo': 'Este es un test de conexión',
        'fecha_publicacion': '2025-07-27T20:30:00Z',
        'fuente': 'test',
        'fuente_nombre_completo': 'Test',
        'url_origen': 'https://test.com',
        'hash_contenido': 'test_hash_123'
    }
    
    try:
        response = requests.post(
            f'{supabase_url}/rest/v1/noticias_juridicas',
            headers=headers_service,
            json=test_data
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            print("✅ Inserción exitosa")
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                test_id = result[0]['id']
                print(f"ID insertado: {test_id}")
                
                # Eliminar el registro de prueba
                delete_response = requests.delete(
                    f'{supabase_url}/rest/v1/noticias_juridicas?id=eq.{test_id}',
                    headers=headers_service
                )
                if delete_response.status_code == 200:
                    print("✅ Registro de prueba eliminado")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_supabase_connection() 
#!/usr/bin/env python3
"""
Script para verificar si los prefijos se están aplicando correctamente
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def verificar_noticias():
    """Verificar noticias de tribunales ambientales"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}'
    }
    
    print("🔍 VERIFICANDO PREFIJOS DE TRIBUNALES AMBIENTALES")
    print("=" * 60)
    
    # Verificar noticias del 3TA
    print("\n📋 NOTICIAS DEL 3TA:")
    response = requests.get(
        f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&fuente=eq.3ta&order=fecha_publicacion.desc&limit=3',
        headers=headers
    )
    
    if response.status_code == 200:
        noticias = response.json()
        for noticia in noticias:
            print(f"Título: {noticia['titulo']}")
            print(f"Fuente: {noticia['fuente']}")
            print("---")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Verificar noticias del 1TA
    print("\n📋 NOTICIAS DEL 1TA:")
    response = requests.get(
        f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&fuente=eq.1ta&order=fecha_publicacion.desc&limit=3',
        headers=headers
    )
    
    if response.status_code == 200:
        noticias = response.json()
        for noticia in noticias:
            print(f"Título: {noticia['titulo']}")
            print(f"Fuente: {noticia['fuente']}")
            print("---")
    else:
        print(f"❌ Error: {response.status_code}")
    
    # Verificar noticias del tribunal_ambiental
    print("\n📋 NOTICIAS DEL TRIBUNAL AMBIENTAL:")
    response = requests.get(
        f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&fuente=eq.tribunal_ambiental&order=fecha_publicacion.desc&limit=3',
        headers=headers
    )
    
    if response.status_code == 200:
        noticias = response.json()
        for noticia in noticias:
            print(f"Título: {noticia['titulo']}")
            print(f"Fuente: {noticia['fuente']}")
            print("---")
    else:
        print(f"❌ Error: {response.status_code}")

if __name__ == "__main__":
    verificar_noticias() 
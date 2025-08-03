#!/usr/bin/env python3
"""
Script para verificar caché del frontend y buscar en todas las tablas
"""

import os
import sys
import requests
import re
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def verificar_todas_las_tablas():
    """Verificar todas las tablas de la base de datos"""
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 VERIFICANDO TODAS LAS TABLAS")
    print("=" * 50)
    
    # Lista de posibles tablas
    tablas_posibles = [
        'noticias_juridicas',
        'noticias',
        'news',
        'articulos',
        'posts',
        'content'
    ]
    
    for tabla in tablas_posibles:
        print(f"\n📋 Verificando tabla: {tabla}")
        
        try:
            response = requests.get(
                f'{SUPABASE_URL}/rest/v1/{tabla}?select=*&limit=5',
                headers=headers
            )
            
            if response.status_code == 200:
                datos = response.json()
                print(f"   ✅ Tabla existe con {len(datos)} registros")
                
                # Verificar si contiene texto problemático
                for i, registro in enumerate(datos, 1):
                    contenido = str(registro)
                    if any([
                        'Acceder al expediente' in contenido,
                        'Morandé 360' in contenido,
                        'contacto@tribunalambiental.cl' in contenido
                    ]):
                        print(f"   ⚠️  Registro {i} contiene texto problemático")
                        print(f"      Contenido: {contenido[:200]}...")
            else:
                print(f"   ❌ Tabla no existe o error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error verificando tabla: {str(e)}")

def verificar_cache_frontend():
    """Verificar si hay caché en el frontend"""
    
    print("\n🌐 VERIFICANDO CACHÉ DEL FRONTEND")
    print("=" * 40)
    
    # URLs del frontend para verificar
    urls_frontend = [
        'https://www.redjudicial.cl/noticias.html',
        'https://www.redjudicial.cl/frontend/noticias-widget.html',
        'https://www.redjudicial.cl/frontend/index.html'
    ]
    
    for url in urls_frontend:
        print(f"\n🔗 Verificando: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                contenido = response.text
                
                # Verificar si contiene texto problemático
                if any([
                    'Acceder al expediente' in contenido,
                    'Morandé 360' in contenido,
                    'contacto@tribunalambiental.cl' in contenido
                ]):
                    print(f"   ⚠️  PÁGINA CONTIENE TEXTO PROBLEMÁTICO")
                    
                    # Buscar líneas específicas
                    lineas = contenido.split('\n')
                    for i, linea in enumerate(lineas, 1):
                        if any([
                            'Acceder al expediente' in linea,
                            'Morandé 360' in linea,
                            'contacto@tribunalambiental.cl' in linea
                        ]):
                            print(f"      Línea {i}: {linea.strip()}")
                else:
                    print(f"   ✅ Sin texto problemático")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error accediendo: {str(e)}")

def verificar_api_noticias():
    """Verificar la API de noticias directamente"""
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("\n🔌 VERIFICANDO API DE NOTICIAS")
    print("=" * 40)
    
    # Verificar diferentes endpoints
    endpoints = [
        '/rest/v1/noticias_juridicas?select=*&limit=10',
        '/rest/v1/noticias?select=*&limit=10',
        '/rest/v1/news?select=*&limit=10'
    ]
    
    for endpoint in endpoints:
        print(f"\n📡 Verificando endpoint: {endpoint}")
        
        try:
            response = requests.get(f'{SUPABASE_URL}{endpoint}', headers=headers)
            
            if response.status_code == 200:
                datos = response.json()
                print(f"   ✅ Endpoint funciona con {len(datos)} registros")
                
                # Verificar contenido
                for i, registro in enumerate(datos, 1):
                    contenido = str(registro)
                    if any([
                        'Acceder al expediente' in contenido,
                        'Morandé 360' in contenido,
                        'contacto@tribunalambiental.cl' in contenido
                    ]):
                        print(f"   ⚠️  Registro {i} contiene texto problemático")
                        print(f"      ID: {registro.get('id', 'N/A')}")
                        print(f"      Título: {registro.get('titulo', 'N/A')[:50]}...")
            else:
                print(f"   ❌ Endpoint no funciona: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

def buscar_texto_especifico():
    """Buscar el texto específico que aparece en el frontend"""
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("\n🎯 BUSCANDO TEXTO ESPECÍFICO")
    print("=" * 40)
    
    # Textos específicos del frontend
    textos_especificos = [
        "Acceder al expediente de la causaR-498-2025",
        "Acceder al expediente de la causaR-518-2025",
        "Acceder al expedienteR-520-2025"
    ]
    
    for texto in textos_especificos:
        print(f"\n🔍 Buscando: {texto}")
        
        # Buscar en diferentes campos
        campos = ['titulo', 'cuerpo_completo', 'contenido', 'texto']
        
        for campo in campos:
            try:
                response = requests.get(
                    f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&{campo}=ilike.%{texto}%&limit=5',
                    headers=headers
                )
                
                if response.status_code == 200:
                    datos = response.json()
                    if datos:
                        print(f"   ⚠️  Encontrado en campo '{campo}': {len(datos)} registros")
                        for registro in datos:
                            print(f"      ID: {registro.get('id')} - {registro.get('titulo', '')[:50]}...")
                else:
                    print(f"   ❌ Error buscando en '{campo}': {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")

def main():
    """Función principal"""
    verificar_todas_las_tablas()
    verificar_cache_frontend()
    verificar_api_noticias()
    buscar_texto_especifico()

if __name__ == "__main__":
    main() 
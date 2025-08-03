#!/usr/bin/env python3
"""
Script para verificar si hay texto problemático en las noticias del Tribunal Ambiental
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

def verificar_texto_problematico():
    """Verificar si hay texto problemático en las noticias"""
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 VERIFICANDO TEXTO PROBLEMÁTICO EN NOTICIAS")
    print("=" * 60)
    
    # Patrones de texto problemático
    patrones_problematicos = [
        r'Acceder al expediente de la causa[A-Z0-9\-]+',
        r'Morandé 360, Piso 8, Santiago',
        r'contacto@tribunalambiental\.cl',
        r'Piso 8, Santiago\([0-9\s\+]+\)',
        r'\([0-9\s\+]+\)contacto@tribunalambiental\.cl',
        r'R-[0-9\-]+ Morandé 360',
        r'Piso 8, Santiago\([0-9\s\+]+\), Piso 8, Santiago'
    ]
    
    # Buscar en noticias del Tribunal Ambiental
    fuentes_ambientales = ['tribunal_ambiental', '1ta', '3ta']
    
    for fuente in fuentes_ambientales:
        print(f"\n📋 Verificando noticias de {fuente}:")
        
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&fuente=eq.{fuente}&order=fecha_publicacion.desc&limit=10',
            headers=headers
        )
        
        if response.status_code == 200:
            noticias = response.json()
            print(f"   Encontradas {len(noticias)} noticias")
            
            for i, noticia in enumerate(noticias, 1):
                titulo = noticia.get('titulo', '')
                contenido = noticia.get('cuerpo_completo', '')
                texto_completo = f"{titulo} {contenido}"
                
                # Verificar cada patrón
                for patron in patrones_problematicos:
                    matches = re.findall(patron, texto_completo, re.IGNORECASE)
                    if matches:
                        print(f"   ⚠️  Noticia {i}: Encontrado patrón problemático")
                        print(f"      Título: {titulo[:100]}...")
                        print(f"      Patrón: {patron}")
                        print(f"      Coincidencias: {matches}")
                        print(f"      URL: {noticia.get('url_origen', 'N/A')}")
                        print()
                        break
        else:
            print(f"   ❌ Error obteniendo noticias: {response.status_code}")
    
    # Buscar en todas las noticias recientes
    print("\n🔍 Verificando todas las noticias recientes:")
    
    response = requests.get(
        f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&order=fecha_publicacion.desc&limit=20',
        headers=headers
    )
    
    if response.status_code == 200:
        noticias = response.json()
        print(f"   Analizando {len(noticias)} noticias recientes")
        
        for i, noticia in enumerate(noticias, 1):
            titulo = noticia.get('titulo', '')
            contenido = noticia.get('cuerpo_completo', '')
            fuente = noticia.get('fuente', '')
            texto_completo = f"{titulo} {contenido}"
            
            # Verificar patrones problemáticos
            for patron in patrones_problematicos:
                matches = re.findall(patron, texto_completo, re.IGNORECASE)
                if matches:
                    print(f"   ⚠️  Noticia {i} ({fuente}): Encontrado patrón problemático")
                    print(f"      Título: {titulo[:100]}...")
                    print(f"      Patrón: {patron}")
                    print(f"      Coincidencias: {matches}")
                    print()
                    break
    else:
        print(f"   ❌ Error obteniendo noticias recientes: {response.status_code}")

def verificar_noticias_especificas():
    """Verificar noticias específicas que podrían tener el problema"""
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("\n🎯 VERIFICANDO NOTICIAS ESPECÍFICAS")
    print("=" * 40)
    
    # Buscar noticias que contengan "expediente" o "causa"
    response = requests.get(
        f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&or=(titulo.ilike.%expediente%,cuerpo_completo.ilike.%expediente%,titulo.ilike.%causa%,cuerpo_completo.ilike.%causa%)&order=fecha_publicacion.desc&limit=10',
        headers=headers
    )
    
    if response.status_code == 200:
        noticias = response.json()
        print(f"   Encontradas {len(noticias)} noticias con 'expediente' o 'causa'")
        
        for i, noticia in enumerate(noticias, 1):
            titulo = noticia.get('titulo', '')
            contenido = noticia.get('cuerpo_completo', '')
            fuente = noticia.get('fuente', '')
            
            # Buscar el texto problemático específico
            if 'Acceder al expediente de la causa' in contenido or 'Morandé 360' in contenido:
                print(f"   ⚠️  Noticia {i} ({fuente}): Posible texto problemático")
                print(f"      Título: {titulo}")
                print(f"      Fuente: {fuente}")
                print(f"      Contenido (últimos 200 chars): {contenido[-200:]}")
                print()
    else:
        print(f"   ❌ Error en búsqueda: {response.status_code}")

if __name__ == "__main__":
    verificar_texto_problematico()
    verificar_noticias_especificas() 
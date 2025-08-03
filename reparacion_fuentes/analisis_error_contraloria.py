#!/usr/bin/env python3
"""
Análisis específico del error de hash duplicado durante scraping de Contraloría
"""

import os
import sys
import requests
import hashlib
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('../APIS_Y_CREDENCIALES.env')

# Configuración de Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://qfomiierchksyfhxoukj.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def analizar_scraper_contraloria():
    """Analizar el scraper de Contraloría para entender el problema"""
    print("🔍 **ANÁLISIS DEL SCRAPER - CONTRALORÍA**")
    print("=" * 60)
    
    scraper_path = "../backend/scrapers/fuentes/contraloria/contraloria_scraper.py"
    
    if not os.path.exists(scraper_path):
        print("❌ Archivo del scraper no encontrado")
        return
    
    try:
        with open(scraper_path, 'r') as f:
            contenido = f.read()
        
        print("✅ Archivo del scraper leído correctamente")
        
        # Buscar funciones de inserción
        if 'insert' in contenido.lower() or 'upsert' in contenido.lower():
            print("✅ Se encontraron funciones de inserción")
        else:
            print("⚠️ No se encontraron funciones de inserción")
        
        # Buscar manejo de errores
        if 'except' in contenido.lower() or 'error' in contenido.lower():
            print("✅ Se encontró manejo de errores")
        else:
            print("⚠️ No se encontró manejo de errores")
        
        # Buscar verificación de duplicados
        if 'duplicate' in contenido.lower() or 'exists' in contenido.lower():
            print("✅ Se encontró verificación de duplicados")
        else:
            print("⚠️ No se encontró verificación de duplicados")
        
        # Mostrar líneas relevantes
        lineas = contenido.split('\n')
        print("\n📋 **LÍNEAS RELEVANTES:**")
        for i, linea in enumerate(lineas):
            if any(palabra in linea.lower() for palabra in ['insert', 'upsert', 'error', 'duplicate', 'hash']):
                print(f"   Línea {i+1}: {linea.strip()}")
                
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")

def analizar_supabase_client():
    """Analizar el cliente de Supabase para entender la inserción"""
    print("\n🔍 **ANÁLISIS DEL CLIENTE SUPABASE**")
    print("=" * 60)
    
    client_path = "../backend/database/supabase_client.py"
    
    if not os.path.exists(client_path):
        print("❌ Archivo del cliente no encontrado")
        return
    
    try:
        with open(client_path, 'r') as f:
            contenido = f.read()
        
        print("✅ Archivo del cliente leído correctamente")
        
        # Buscar funciones de inserción
        if 'insert' in contenido.lower():
            print("✅ Se encontraron funciones de inserción")
        else:
            print("⚠️ No se encontraron funciones de inserción")
        
        # Buscar manejo de errores de duplicado
        if '23505' in contenido or 'duplicate' in contenido.lower():
            print("✅ Se encontró manejo de errores de duplicado")
        else:
            print("⚠️ No se encontró manejo de errores de duplicado")
        
        # Mostrar líneas relevantes
        lineas = contenido.split('\n')
        print("\n📋 **LÍNEAS RELEVANTES:**")
        for i, linea in enumerate(lineas):
            if any(palabra in linea.lower() for palabra in ['insert', '23505', 'duplicate', 'error']):
                print(f"   Línea {i+1}: {linea.strip()}")
                
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")

def simular_error_hash():
    """Simular el error de hash duplicado"""
    print("\n🧪 **SIMULACIÓN DE ERROR DE HASH**")
    print("=" * 60)
    
    # Obtener noticias existentes de Contraloría
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}'
        }
        
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&fuente=eq.contraloria&order=fecha_publicacion.desc&limit=5',
            headers=headers
        )
        
        if response.status_code == 200:
            noticias = response.json()
            print(f"✅ Obtenidas {len(noticias)} noticias de Contraloría")
            
            # Intentar insertar una noticia existente
            if noticias:
                noticia_existente = noticias[0]
                
                # Crear datos para inserción
                datos_insercion = {
                    'titulo': noticia_existente['titulo'],
                    'contenido': noticia_existente['contenido'],
                    'url_origen': noticia_existente['url_origen'],
                    'fuente': 'contraloria',
                    'fecha_publicacion': noticia_existente['fecha_publicacion'],
                    'hash_contenido': noticia_existente['hash_contenido']
                }
                
                print("🔍 Intentando insertar noticia duplicada...")
                
                # Intentar inserción
                response_insert = requests.post(
                    f'{SUPABASE_URL}/rest/v1/noticias_juridicas',
                    headers={
                        **headers,
                        'Content-Type': 'application/json',
                        'Prefer': 'return=minimal'
                    },
                    json=datos_insercion
                )
                
                if response_insert.status_code == 409:
                    print("✅ Error 409 (duplicado) reproducido correctamente")
                    print(f"   Error: {response_insert.text}")
                else:
                    print(f"⚠️ Respuesta inesperada: {response_insert.status_code}")
                    print(f"   Respuesta: {response_insert.text}")
                    
        else:
            print(f"❌ Error obteniendo noticias: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en simulación: {e}")

def analizar_logs_scraping():
    """Analizar logs del scraping para entender el problema"""
    print("\n📋 **ANÁLISIS DE LOGS DE SCRAPING**")
    print("=" * 60)
    
    # Buscar archivos de log
    logs_dir = "../logs" if os.path.exists("../logs") else "."
    
    archivos_log = []
    for archivo in os.listdir(logs_dir):
        if archivo.endswith('.log') or 'log' in archivo.lower():
            archivos_log.append(os.path.join(logs_dir, archivo))
    
    if archivos_log:
        print(f"✅ Encontrados {len(archivos_log)} archivos de log")
        
        for archivo in archivos_log:
            print(f"\n📄 Analizando: {archivo}")
            try:
                with open(archivo, 'r') as f:
                    contenido = f.read()
                
                # Buscar errores de Contraloría
                if 'contraloria' in contenido.lower():
                    print("✅ Se encontraron referencias a Contraloría")
                    
                    # Buscar errores específicos
                    if '23505' in contenido or 'duplicate' in contenido.lower():
                        print("✅ Se encontraron errores de duplicado")
                        
                        # Mostrar líneas con errores
                        lineas = contenido.split('\n')
                        for i, linea in enumerate(lineas):
                            if '23505' in linea or 'duplicate' in linea.lower():
                                print(f"   Línea {i+1}: {linea.strip()}")
                    else:
                        print("⚠️ No se encontraron errores de duplicado")
                else:
                    print("⚠️ No se encontraron referencias a Contraloría")
                    
            except Exception as e:
                print(f"❌ Error leyendo archivo: {e}")
    else:
        print("⚠️ No se encontraron archivos de log")

def generar_solucion_hash():
    """Generar solución para el problema de hash duplicado"""
    print("\n💡 **SOLUCIÓN PARA ERROR DE HASH DUPLICADO**")
    print("=" * 60)
    
    print("🔧 **PROBLEMA IDENTIFICADO:**")
    print("   - El scraper intenta insertar noticias que ya existen")
    print("   - No hay verificación de duplicados antes de insertar")
    print("   - El error 409 (duplicado) no se maneja correctamente")
    
    print("\n🔧 **SOLUCIÓN PROPUESTA:**")
    print("1. **Verificación previa de duplicados:**")
    print("   - Buscar noticia existente por URL antes de insertar")
    print("   - Verificar por título y fecha si la URL no existe")
    print("   - Usar hash como respaldo, no como único identificador")
    
    print("\n2. **Manejo de errores de duplicado:**")
    print("   - Capturar error 409 (duplicado)")
    print("   - Actualizar noticia existente en lugar de fallar")
    print("   - Logging informativo en lugar de error")
    
    print("\n3. **Mejora en la lógica de inserción:**")
    print("   - Implementar upsert (insert or update)")
    print("   - Verificar existencia antes de intentar inserción")
    print("   - Manejo graceful de duplicados")
    
    print("\n4. **Código de ejemplo:**")
    print("""
    # Verificar si la noticia ya existe
    noticia_existente = buscar_noticia_por_url(url)
    if noticia_existente:
        # Actualizar noticia existente
        actualizar_noticia(noticia_existente['id'], datos_nuevos)
    else:
        # Insertar nueva noticia
        insertar_noticia(datos_nuevos)
    """)

def main():
    """Función principal"""
    print("🔍 **ANÁLISIS ESPECÍFICO - ERROR HASH CONTRALORÍA**")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Ejecutar análisis
    analizar_scraper_contraloria()
    analizar_supabase_client()
    simular_error_hash()
    analizar_logs_scraping()
    generar_solucion_hash()
    
    print(f"\n✅ **ANÁLISIS COMPLETADO**")
    print("=" * 70)

if __name__ == "__main__":
    main() 
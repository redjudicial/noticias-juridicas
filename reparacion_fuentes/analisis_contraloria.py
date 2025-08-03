#!/usr/bin/env python3
"""
Análisis específico del problema de hash duplicado en Contraloría
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

def obtener_noticias_contraloria():
    """Obtener noticias de Contraloría de la base de datos"""
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}'
        }
        
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&fuente=eq.contraloria&order=fecha_publicacion.desc',
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error al obtener noticias: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return []

def analizar_hashes_duplicados():
    """Analizar hashes duplicados en noticias de Contraloría"""
    print("🔍 **ANÁLISIS DE HASHES DUPLICADOS - CONTRALORÍA**")
    print("=" * 60)
    
    noticias = obtener_noticias_contraloria()
    
    if not noticias:
        print("❌ No se pudieron obtener noticias de Contraloría")
        return
    
    print(f"📊 Total noticias de Contraloría: {len(noticias)}")
    
    # Analizar hashes
    hashes = {}
    duplicados = []
    
    for noticia in noticias:
        hash_contenido = noticia.get('hash_contenido')
        titulo = noticia.get('titulo', 'Sin título')
        fecha = noticia.get('fecha_publicacion', 'Sin fecha')
        url = noticia.get('url_origen', 'Sin URL')
        
        if hash_contenido:
            if hash_contenido in hashes:
                duplicados.append({
                    'hash': hash_contenido,
                    'titulo1': hashes[hash_contenido]['titulo'],
                    'fecha1': hashes[hash_contenido]['fecha'],
                    'url1': hashes[hash_contenido]['url'],
                    'titulo2': titulo,
                    'fecha2': fecha,
                    'url2': url
                })
            else:
                hashes[hash_contenido] = {
                    'titulo': titulo,
                    'fecha': fecha,
                    'url': url
                }
    
    print(f"\n📊 **ANÁLISIS DE DUPLICADOS:**")
    print("-" * 40)
    print(f"Total noticias: {len(noticias)}")
    print(f"Hashes únicos: {len(hashes)}")
    print(f"Duplicados encontrados: {len(duplicados)}")
    
    if duplicados:
        print(f"\n🚨 **DUPLICADOS DETECTADOS:**")
        print("-" * 40)
        for i, dup in enumerate(duplicados[:10], 1):  # Mostrar solo los primeros 10
            print(f"{i}. Hash: {dup['hash'][:20]}...")
            print(f"   Noticia 1: {dup['titulo1'][:50]}... ({dup['fecha1'][:10]})")
            print(f"   Noticia 2: {dup['titulo2'][:50]}... ({dup['fecha2'][:10]})")
            print(f"   URLs: {dup['url1'] != dup['url2']}")
            print()
    
    return duplicados

def analizar_fechas_contraloria():
    """Analizar fechas de las noticias de Contraloría"""
    print("\n📅 **ANÁLISIS DE FECHAS - CONTRALORÍA**")
    print("-" * 40)
    
    noticias = obtener_noticias_contraloria()
    
    if not noticias:
        return
    
    # Agrupar por fecha
    fechas = {}
    for noticia in noticias:
        fecha = noticia.get('fecha_publicacion', 'Sin fecha')
        if fecha != 'Sin fecha':
            fecha_simple = fecha[:10]  # Solo la fecha
            if fecha_simple not in fechas:
                fechas[fecha_simple] = 0
            fechas[fecha_simple] += 1
    
    print("📊 Noticias por fecha:")
    for fecha in sorted(fechas.keys(), reverse=True):
        print(f"  {fecha}: {fechas[fecha]} noticias")
    
    # Verificar la última noticia
    if noticias:
        ultima = noticias[0]
        fecha_ultima = datetime.fromisoformat(ultima['fecha_publicacion'].replace('Z', '+00:00'))
        ahora = datetime.now(fecha_ultima.tzinfo)
        diferencia = ahora - fecha_ultima
        
        print(f"\n⏰ Última noticia: {fecha_ultima.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏰ Tiempo transcurrido: {diferencia}")
        
        if diferencia.days > 1:
            print("⚠️ ¡ALERTA! No hay noticias nuevas en más de 1 día")

def verificar_urls_contraloria():
    """Verificar que las URLs de Contraloría siguen siendo válidas"""
    print("\n🔗 **VERIFICACIÓN DE URLs - CONTRALORÍA**")
    print("-" * 40)
    
    noticias = obtener_noticias_contraloria()
    
    if not noticias:
        return
    
    # Tomar las últimas 5 noticias para verificar
    noticias_recientes = noticias[:5]
    
    print("🔍 Verificando URLs de las últimas 5 noticias:")
    
    for i, noticia in enumerate(noticias_recientes, 1):
        url = noticia.get('url_origen', '')
        titulo = noticia.get('titulo', 'Sin título')
        
        if url:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"✅ {i}. {titulo[:40]}... - URL válida")
                else:
                    print(f"❌ {i}. {titulo[:40]}... - Error {response.status_code}")
            except Exception as e:
                print(f"❌ {i}. {titulo[:40]}... - Error de conexión: {e}")
        else:
            print(f"⚠️ {i}. {titulo[:40]}... - Sin URL")

def analizar_estructura_hash():
    """Analizar cómo se genera el hash en Contraloría"""
    print("\n🔧 **ANÁLISIS DE GENERACIÓN DE HASH**")
    print("-" * 40)
    
    # Buscar el scraper de Contraloría
    scraper_path = "../backend/scrapers/fuentes/contraloria/contraloria_scraper.py"
    
    if os.path.exists(scraper_path):
        print("✅ Archivo del scraper encontrado")
        
        try:
            with open(scraper_path, 'r') as f:
                contenido = f.read()
            
            # Buscar funciones relacionadas con hash
            if 'hash' in contenido.lower():
                print("✅ Código de hash encontrado en el scraper")
                
                # Buscar líneas específicas
                lineas = contenido.split('\n')
                for i, linea in enumerate(lineas):
                    if 'hash' in linea.lower():
                        print(f"   Línea {i+1}: {linea.strip()}")
            else:
                print("⚠️ No se encontró código de hash en el scraper")
                
        except Exception as e:
            print(f"❌ Error leyendo archivo: {e}")
    else:
        print("❌ Archivo del scraper no encontrado")

def generar_recomendaciones():
    """Generar recomendaciones específicas para Contraloría"""
    print("\n💡 **RECOMENDACIONES PARA CONTRALORÍA**")
    print("-" * 40)
    
    print("1. 🔧 **PROBLEMA DE HASH DUPLICADO:**")
    print("   - Revisar lógica de generación de hash")
    print("   - Verificar que el hash incluya elementos únicos")
    print("   - Implementar verificación de duplicados antes de insertar")
    
    print("\n2. 🔍 **VERIFICACIÓN DE DUPLICADOS:**")
    print("   - Buscar noticias existentes por URL antes de insertar")
    print("   - Implementar verificación por título y fecha")
    print("   - Usar hash como respaldo, no como único identificador")
    
    print("\n3. 📅 **ACTUALIZACIÓN DE FECHAS:**")
    print("   - Verificar que las fechas se extraen correctamente")
    print("   - Implementar filtro por fecha para evitar noticias antiguas")
    print("   - Agregar logging para monitorear fechas extraídas")
    
    print("\n4. 🔗 **VERIFICACIÓN DE URLs:**")
    print("   - Verificar que las URLs siguen siendo válidas")
    print("   - Implementar manejo de errores para URLs rotas")
    print("   - Agregar timeout y reintentos para conexiones")

def main():
    """Función principal"""
    print("🔍 **ANÁLISIS ESPECÍFICO - CONTRALORÍA**")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Ejecutar análisis
    duplicados = analizar_hashes_duplicados()
    analizar_fechas_contraloria()
    verificar_urls_contraloria()
    analizar_estructura_hash()
    generar_recomendaciones()
    
    print(f"\n✅ **ANÁLISIS COMPLETADO**")
    print("=" * 70)
    
    if duplicados:
        print(f"🚨 Se encontraron {len(duplicados)} duplicados que necesitan atención")
    else:
        print("✅ No se encontraron duplicados")

if __name__ == "__main__":
    main() 
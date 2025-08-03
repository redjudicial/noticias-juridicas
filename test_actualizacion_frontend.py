#!/usr/bin/env python3
"""
Script para probar la actualización automática del frontend
"""

import requests
import json
import time
from datetime import datetime

# Configuración de Supabase
SUPABASE_URL = 'https://qfomiierchksyfhxoukj.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFmb21paWVyY2hrc3lmaHhvdWtqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEwMjgxNTYsImV4cCI6MjA2NjYwNDE1Nn0.HqlptdYXjd2s9q8xHEmgQPyf6a95fosb0YT5b4asMA8'

def obtener_noticias():
    """Obtener noticias desde Supabase"""
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&order=fecha_publicacion.desc&limit=10',
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error al obtener noticias: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return None

def verificar_actualizacion():
    """Verificar si hay actualizaciones en las noticias"""
    print("🔍 **VERIFICACIÓN DE ACTUALIZACIÓN AUTOMÁTICA**")
    print("=" * 50)
    
    # Primera consulta
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    noticias1 = obtener_noticias()
    
    if not noticias1:
        print("❌ No se pudieron obtener noticias")
        return
    
    print(f"📊 Noticias obtenidas: {len(noticias1)}")
    if noticias1:
        print(f"📰 Última noticia: {noticias1[0]['titulo'][:50]}...")
        print(f"🕐 Fecha: {noticias1[0]['fecha_publicacion']}")
    
    # Esperar 30 segundos
    print("\n⏳ Esperando 30 segundos para verificar cambios...")
    time.sleep(30)
    
    # Segunda consulta
    print(f"\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    noticias2 = obtener_noticias()
    
    if not noticias2:
        print("❌ No se pudieron obtener noticias en la segunda consulta")
        return
    
    print(f"📊 Noticias obtenidas: {len(noticias2)}")
    if noticias2:
        print(f"📰 Última noticia: {noticias2[0]['titulo'][:50]}...")
        print(f"🕐 Fecha: {noticias2[0]['fecha_publicacion']}")
    
    # Comparar resultados
    print("\n🔍 **COMPARACIÓN:**")
    if len(noticias1) != len(noticias2):
        print(f"✅ Cambio detectado: {len(noticias1)} → {len(noticias2)} noticias")
    else:
        print(f"📊 Mismo número de noticias: {len(noticias1)}")
    
    if noticias1 and noticias2:
        if noticias1[0]['id'] != noticias2[0]['id']:
            print("✅ Nueva noticia detectada en la primera posición")
        else:
            print("📊 Misma noticia en la primera posición")
            
        # Verificar fechas
        fecha1 = noticias1[0]['fecha_publicacion']
        fecha2 = noticias2[0]['fecha_publicacion']
        if fecha1 != fecha2:
            print(f"✅ Cambio de fecha detectado: {fecha1} → {fecha2}")
        else:
            print(f"📊 Misma fecha: {fecha1}")

def probar_cache_navegador():
    """Probar si hay problemas de cache en el navegador"""
    print("\n🌐 **PRUEBA DE CACHE DEL NAVEGADOR**")
    print("=" * 50)
    
    # Simular petición con diferentes headers
    headers_variaciones = [
        {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        },
        {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Cache-Control': 'max-age=0'
        },
        {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}'
        }
    ]
    
    for i, headers in enumerate(headers_variaciones, 1):
        print(f"\n🔍 Prueba {i}: Headers de cache diferentes")
        try:
            response = requests.get(
                f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&order=fecha_publicacion.desc&limit=1',
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    print(f"✅ Respuesta exitosa: {data[0]['titulo'][:30]}...")
                    print(f"🕐 Fecha: {data[0]['fecha_publicacion']}")
                else:
                    print("⚠️ Respuesta vacía")
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print("🚀 **INICIANDO PRUEBAS DE ACTUALIZACIÓN**")
    print("=" * 60)
    
    # Verificar actualización
    verificar_actualizacion()
    
    # Probar cache
    probar_cache_navegador()
    
    print("\n✅ **PRUEBAS COMPLETADAS**")
    print("=" * 60)

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Script para limpiar completamente la tabla de noticias en Supabase
PASO 2 del pipeline: Limpiar tabla antes de extracción completa
"""

import sys
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database.supabase_client import SupabaseClient

def limpiar_tabla_noticias():
    """Limpiar completamente la tabla de noticias"""
    print("🧹 **PASO 2: LIMPIANDO TABLA DE NOTICIAS**")
    print("=" * 50)
    
    # Inicializar Supabase con credenciales
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Error: Faltan credenciales de Supabase")
        return
    
    supabase = SupabaseClient(supabase_url, supabase_key)
    
    # Verificar conexión
    print("🔍 Verificando conexión a Supabase...")
    if not supabase.test_connection():
        print("❌ Error: No se puede conectar a Supabase")
        return
    
    print("✅ Conexión exitosa")
    
    # Contar noticias actuales
    print("\n📊 Contando noticias actuales...")
    try:
        count = supabase.count_noticias()
        print(f"📈 Noticias actuales en la tabla: {count}")
        
        if count == 0:
            print("✅ La tabla ya está vacía")
            return
            
    except Exception as e:
        print(f"❌ Error contando noticias: {e}")
        return
    
    # Confirmar limpieza
    print(f"\n⚠️  ¿Estás seguro de que quieres eliminar TODAS las {count} noticias?")
    print("Esta acción NO se puede deshacer.")
    
    confirmacion = input("Escribe 'SI' para confirmar: ")
    
    if confirmacion != 'SI':
        print("❌ Operación cancelada")
        return
    
    # Limpiar tabla
    print("\n🧹 Limpiando tabla...")
    try:
        # Usar el método de limpieza de Supabase
        eliminadas = supabase.limpiar_noticias_duplicadas()
        print(f"✅ Eliminadas {eliminadas} noticias duplicadas")
        
        # Eliminar todas las noticias restantes usando SQL directo
        import requests
        response = requests.post(
            f'{supabase.url}/rest/v1/rpc/limpiar_tabla_noticias',
            headers=supabase.headers,
            json={}
        )
        
        if response.status_code == 200:
            print("✅ Tabla limpiada completamente")
        else:
            # Si no existe la función RPC, usar DELETE con condición más específica
            print("⚠️  Intentando método alternativo...")
            response = requests.delete(
                f'{supabase.url}/rest/v1/noticias_juridicas?titulo=not.is.null',
                headers=supabase.headers
            )
            
            if response.status_code == 200:
                print("✅ Tabla limpiada completamente")
            else:
                print(f"❌ Error limpiando tabla: {response.status_code} - {response.text}")
                return
            
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        return
    
    # Verificar que la tabla esté vacía
    print("\n🔍 Verificando limpieza...")
    try:
        count_final = supabase.count_noticias()
        print(f"📊 Noticias restantes: {count_final}")
        
        if count_final == 0:
            print("✅ Tabla limpiada exitosamente")
        else:
            print(f"⚠️  Aún quedan {count_final} noticias")
            
    except Exception as e:
        print(f"❌ Error verificando limpieza: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 **PASO 2 COMPLETADO**")

if __name__ == "__main__":
    limpiar_tabla_noticias() 
#!/usr/bin/env python3
"""
Script automatizado para crear la tabla noticias_juridicas en Supabase
"""
import os
import sys
import requests
import time
from pathlib import Path

# Agregar el directorio padre al path para importar las credenciales
sys.path.append(str(Path(__file__).parent.parent.parent))

def load_env_vars():
    """Cargar variables de entorno desde el archivo APIS_Y_CREDENCIALES.env"""
    env_file = Path(__file__).parent.parent.parent / 'APIS_Y_CREDENCIALES.env'
    
    if not env_file.exists():
        print("❌ Error: No se encontró el archivo APIS_Y_CREDENCIALES.env")
        print(f"Buscando en: {env_file}")
        return None
    
    env_vars = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
    
    return env_vars

def create_table_in_supabase():
    """Crear la tabla noticias_juridicas en Supabase"""
    
    # Cargar variables de entorno
    env_vars = load_env_vars()
    if not env_vars:
        return False
    
    SUPABASE_URL = env_vars.get('SUPABASE_URL')
    SUPABASE_SERVICE_KEY = env_vars.get('SUPABASE_SERVICE_ROLE_KEY')
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("❌ Error: Faltan credenciales de Supabase en el archivo .env")
        return False
    
    print(f"🚀 Conectando a Supabase: {SUPABASE_URL}")
    
    # Leer el schema SQL
    schema_file = Path(__file__).parent / 'schema.sql'
    if not schema_file.exists():
        print("❌ Error: No se encontró el archivo schema.sql")
        return False
    
    with open(schema_file, 'r') as f:
        sql_content = f.read()
    
    # Headers para Supabase
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    # Dividir comandos SQL y ejecutarlos uno por uno
    commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
    
    print(f"📋 Ejecutando {len(commands)} comandos SQL...")
    
    success_count = 0
    error_count = 0
    
    for i, command in enumerate(commands, 1):
        if command:
            try:
                print(f"⏳ Ejecutando comando {i}/{len(commands)}...")
                
                # Usar la función exec_sql de Supabase
                response = requests.post(
                    f'{SUPABASE_URL}/rest/v1/rpc/exec_sql',
                    headers=headers,
                    json={'sql': command},
                    timeout=30
                )
                
                if response.status_code == 200:
                    print(f"✅ Comando {i} ejecutado exitosamente")
                    success_count += 1
                else:
                    print(f"❌ Error en comando {i}: {response.status_code}")
                    print(f"Response: {response.text[:200]}...")
                    error_count += 1
                
                # Pequeña pausa para no sobrecargar la API
                time.sleep(0.5)
                    
            except Exception as e:
                print(f"❌ Error ejecutando comando {i}: {e}")
                error_count += 1
    
    print(f"\n📊 Resumen:")
    print(f"✅ Comandos exitosos: {success_count}")
    print(f"❌ Comandos con error: {error_count}")
    
    if error_count == 0:
        print("🎉 ¡Tabla creada exitosamente!")
        return True
    else:
        print("⚠️  Algunos comandos fallaron. Revisa los errores arriba.")
        return False

def test_connection():
    """Probar la conexión a Supabase"""
    env_vars = load_env_vars()
    if not env_vars:
        return False
    
    SUPABASE_URL = env_vars.get('SUPABASE_URL')
    SUPABASE_ANON_KEY = env_vars.get('SUPABASE_ANON_KEY')
    
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("❌ Error: Faltan credenciales de Supabase")
        return False
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}'
    }
    
    try:
        response = requests.get(f'{SUPABASE_URL}/rest/v1/', headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Conexión a Supabase exitosa")
            return True
        else:
            print(f"❌ Error de conexión: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def insert_test_data():
    """Insertar datos de prueba"""
    env_vars = load_env_vars()
    if not env_vars:
        return False
    
    SUPABASE_URL = env_vars.get('SUPABASE_URL')
    SUPABASE_SERVICE_KEY = env_vars.get('SUPABASE_SERVICE_ROLE_KEY')
    
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    test_data = [
        {
            'titulo': 'Corte Suprema confirma sentencia en caso emblemático',
            'resumen': 'La Corte Suprema confirmó la sentencia del tribunal de primera instancia en un caso que ha generado gran interés público.',
            'fecha_publicacion': '2025-01-27T10:00:00Z',
            'fuente': 'poder_judicial',
            'categoria': 'fallos',
            'link_origen': 'https://www.pjud.cl/noticia-ejemplo',
            'hash_contenido': 'hash_test_1'
        },
        {
            'titulo': 'Ministerio de Justicia anuncia nueva política de transparencia',
            'resumen': 'El Ministerio de Justicia presentó una nueva política de transparencia que mejorará el acceso a la información pública.',
            'fecha_publicacion': '2025-01-27T09:00:00Z',
            'fuente': 'minjusticia',
            'categoria': 'institucional',
            'link_origen': 'https://www.minjusticia.gob.cl/noticia-ejemplo',
            'hash_contenido': 'hash_test_2'
        },
        {
            'titulo': 'Fiscalía Regional obtiene condena en caso de corrupción',
            'resumen': 'La Fiscalía Regional de Santiago logró una importante condena en un caso de corrupción que involucraba a funcionarios públicos.',
            'fecha_publicacion': '2025-01-27T08:00:00Z',
            'fuente': 'fiscalia',
            'categoria': 'penal',
            'link_origen': 'https://www.fiscaliadechile.cl/noticia-ejemplo',
            'hash_contenido': 'hash_test_3'
        }
    ]
    
    print("📝 Insertando datos de prueba...")
    
    for data in test_data:
        try:
            response = requests.post(
                f'{SUPABASE_URL}/rest/v1/noticias_juridicas',
                headers=headers,
                json=data
            )
            
            if response.status_code == 201:
                print(f"✅ Dato insertado: {data['titulo'][:50]}...")
            else:
                print(f"❌ Error insertando: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("✅ Datos de prueba insertados")

if __name__ == "__main__":
    print("🔧 Script de creación de tabla noticias_juridicas")
    print("=" * 50)
    
    # Probar conexión
    if not test_connection():
        print("❌ No se pudo conectar a Supabase. Verifica las credenciales.")
        sys.exit(1)
    
    # Crear tabla
    if create_table_in_supabase():
        print("\n🎯 Tabla creada exitosamente!")
        
        # Insertar datos de prueba
        print("\n📝 Insertando datos de prueba...")
        insert_test_data()
        
        print("\n✅ ¡Proceso completado!")
        print("\n🔗 Puedes probar el frontend ahora:")
        print("   - Abre frontend/index.html en tu navegador")
        print("   - O usa frontend/noticias-widget.html para el widget")
        
    else:
        print("❌ Error creando la tabla")
        sys.exit(1) 
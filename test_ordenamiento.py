#!/usr/bin/env python3
"""
Script de prueba para verificar el ordenamiento personalizado
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timezone

load_dotenv('APIS_Y_CREDENCIALES.env')

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
supabase: Client = create_client(url, key)

def ordenar_noticias_personalizado(noticias):
    """
    Simula la lógica de ordenamiento del JavaScript
    """
    def comparar(a, b):
        # Ordenar por fecha descendente, pero Tribunal Ambiental al final
        fechaA = datetime.fromisoformat(a['fecha_publicacion'].replace('Z', '+00:00'))
        fechaB = datetime.fromisoformat(b['fecha_publicacion'].replace('Z', '+00:00'))
        
        # Si ambas son del Tribunal Ambiental, ordenar por fecha
        if a['fuente'] == 'tribunal_ambiental' and b['fuente'] == 'tribunal_ambiental':
            if fechaB > fechaA:
                return -1
            elif fechaB < fechaA:
                return 1
            else:
                return 0
        
        # Si solo A es del Tribunal Ambiental, ponerla al final
        if a['fuente'] == 'tribunal_ambiental':
            return 1
        
        # Si solo B es del Tribunal Ambiental, ponerla al final
        if b['fuente'] == 'tribunal_ambiental':
            return -1
        
        # Para el resto, ordenar por fecha descendente
        if fechaB > fechaA:
            return -1
        elif fechaB < fechaA:
            return 1
        else:
            return 0
    
    from functools import cmp_to_key
    return sorted(noticias, key=cmp_to_key(comparar))

# Obtener las últimas 20 noticias
result = supabase.table('noticias_juridicas').select('id, titulo, fuente, fecha_publicacion').order('fecha_publicacion', desc=True).limit(20).execute()

print("=== ORDENAMIENTO ORIGINAL (por fecha) ===")
for i, noticia in enumerate(result.data[:10], 1):
    fecha = noticia['fecha_publicacion']
    print(f'{i}. {fecha} - {noticia["fuente"]} - {noticia["titulo"][:40]}...')

print("\n=== ORDENAMIENTO PERSONALIZADO (Tribunal Ambiental al final) ===")
noticias_ordenadas = ordenar_noticias_personalizado(result.data)
for i, noticia in enumerate(noticias_ordenadas[:10], 1):
    fecha = noticia['fecha_publicacion']
    print(f'{i}. {fecha} - {noticia["fuente"]} - {noticia["titulo"][:40]}...')

print("\n=== RESUMEN ===")
fuentes_original = [n['fuente'] for n in result.data[:10]]
fuentes_personalizado = [n['fuente'] for n in noticias_ordenadas[:10]]

print("Primeras 10 fuentes (original):", fuentes_original)
print("Primeras 10 fuentes (personalizado):", fuentes_personalizado)

# Verificar si Tribunal Ambiental está al final
tribunales_original = [i for i, f in enumerate(fuentes_original) if 'tribunal' in f.lower()]
tribunales_personalizado = [i for i, f in enumerate(fuentes_personalizado) if 'tribunal' in f.lower()]

print(f"\nPosiciones de tribunales ambientales:")
print(f"Original: {tribunales_original}")
print(f"Personalizado: {tribunales_personalizado}")

if tribunales_personalizado and max(tribunales_personalizado) > 5:
    print("✅ Tribunal Ambiental está al final en el ordenamiento personalizado")
else:
    print("❌ Tribunal Ambiental NO está al final") 
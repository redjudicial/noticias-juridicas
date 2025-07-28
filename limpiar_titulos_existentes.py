#!/usr/bin/env python3
"""
Script para limpiar títulos existentes en la base de datos
"""

import os
import requests
import re
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

def limpiar_titulo(titulo: str) -> str:
    """Limpiar título de fechas y horas"""
    if not titulo:
        return ""
    
    titulo_limpio = titulo
    
    # Patrones de fecha y hora más agresivos
    patrones_fecha_hora = [
        r'\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}',  # DD-MM-YYYY HH:MM
        r'\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}',  # DD/MM/YYYY HH:MM
        r'\d{2}:\d{2}',  # Solo hora
        r'\d{2}-\d{2}-\d{4}',  # Solo fecha DD-MM-YYYY
        r'\d{2}/\d{2}/\d{4}',  # Solo fecha DD/MM/YYYY
        r'\d{4}-\d{2}-\d{2}',  # Solo fecha YYYY-MM-DD
        r'\d{1,2}-\d{1,2}-\d{4}\s+\d{1,2}:\d{2}',  # D-M-YYYY H:MM
        r'\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}',  # D/M/YYYY H:MM
        r'\d{1,2}-\d{1,2}-\d{4}',  # D-M-YYYY
        r'\d{1,2}/\d{1,2}/\d{4}',  # D/M/YYYY
        # Patrones específicos para el ejemplo dado
        r'\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}$',  # 26-07-2025 04:07
        r'\d{2}-\d{2}-\d{4}\s+\d{1,2}:\d{2}$',  # 26-07-2025 4:07
        r'\d{1,2}-\d{1,2}-\d{4}\s+\d{2}:\d{2}$',  # 6-07-2025 04:07
        r'\d{1,2}-\d{1,2}-\d{4}\s+\d{1,2}:\d{2}$',  # 6-7-2025 4:07
    ]
    
    for patron in patrones_fecha_hora:
        titulo_limpio = re.sub(patron, '', titulo_limpio)
    
    # Limpiar espacios múltiples
    titulo_limpio = re.sub(r'\s+', ' ', titulo_limpio)
    titulo_limpio = titulo_limpio.strip()
    
    return titulo_limpio

def limpiar_titulos_existentes():
    """Limpiar títulos existentes en la base de datos"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("🧹 **LIMPIANDO TÍTULOS EXISTENTES**")
    print("=" * 50)
    
    # Obtener noticias con títulos que contengan fechas
    try:
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=id,titulo,fuente&order=fecha_publicacion.desc',
            headers=headers
        )
        
        if response.status_code == 200:
            noticias = response.json()
            
            titulos_limpiados = 0
            
            for noticia in noticias:
                titulo_original = noticia.get('titulo', '')
                titulo_limpio = limpiar_titulo(titulo_original)
                
                # Si el título cambió, actualizarlo
                if titulo_limpio != titulo_original and titulo_limpio:
                    print(f"🔄 Limpiando: {titulo_original[:60]}...")
                    print(f"   → {titulo_limpio[:60]}...")
                    
                    # Actualizar título
                    update_data = {'titulo': titulo_limpio}
                    
                    update_response = requests.patch(
                        f'{SUPABASE_URL}/rest/v1/noticias_juridicas?id=eq.{noticia["id"]}',
                        headers=headers,
                        json=update_data
                    )
                    
                    if update_response.status_code == 200:
                        titulos_limpiados += 1
                        print(f"   ✅ Actualizado")
                    else:
                        print(f"   ❌ Error: {update_response.status_code}")
                    
                    print()
            
            print(f"🎯 **RESUMEN:**")
            print(f"   • Títulos limpiados: {titulos_limpiados}")
            print(f"   • Total noticias revisadas: {len(noticias)}")
            
        else:
            print(f"❌ Error obteniendo noticias: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    limpiar_titulos_existentes() 
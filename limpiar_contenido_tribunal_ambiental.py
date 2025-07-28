#!/usr/bin/env python3
"""
Limpiar información de contacto duplicada del Tribunal Ambiental
"""

import os
import requests
import re
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

def limpiar_contenido_tribunal_ambiental():
    """Limpiar contenido problemático del Tribunal Ambiental"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("🧹 **LIMPIANDO CONTENIDO TRIBUNAL AMBIENTAL**")
    print("=" * 50)
    
    try:
        # Obtener noticias del Tribunal Ambiental
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&fuente=eq.tribunal_ambiental&order=fecha_publicacion.desc',
            headers=headers
        )
        
        if response.status_code == 200:
            noticias = response.json()
            
            print(f"📊 Noticias del Tribunal Ambiental: {len(noticias)}")
            
            for noticia in noticias:
                contenido_original = noticia.get('cuerpo_completo', '')
                titulo = noticia.get('titulo', '')
                
                # Limpiar información de contacto duplicada
                contenido_limpio = contenido_original
                
                # Patrones a eliminar
                patrones_limpiar = [
                    r'Acceder al expediente.*?contacto@tribunalambiental\.cl\.',
                    r'Morandé 360, Piso 8, Santiago.*?contacto@tribunalambiental\.cl\.',
                    r'\(\d{2}\) \d{1,2} \d{3,4} \d{2,4}.*?contacto@tribunalambiental\.cl\.',
                    r'Piso 8, Santiago.*?contacto@tribunalambiental\.cl\.',
                ]
                
                for patron in patrones_limpiar:
                    contenido_limpio = re.sub(patron, '', contenido_limpio, flags=re.DOTALL)
                
                # Limpiar espacios múltiples
                contenido_limpio = re.sub(r'\s+', ' ', contenido_limpio)
                contenido_limpio = contenido_limpio.strip()
                
                # Si el contenido cambió, actualizarlo
                if contenido_limpio != contenido_original and contenido_limpio:
                    print(f"🔄 Limpiando: {titulo[:50]}...")
                    
                    # Actualizar contenido
                    update_data = {'cuerpo_completo': contenido_limpio}
                    
                    update_response = requests.patch(
                        f'{SUPABASE_URL}/rest/v1/noticias_juridicas?id=eq.{noticia["id"]}',
                        headers=headers,
                        json=update_data
                    )
                    
                    if update_response.status_code == 200:
                        print(f"   ✅ Contenido limpiado")
                    else:
                        print(f"   ❌ Error: {update_response.status_code}")
                    
                    print()
            
            print("✅ Limpieza completada")
            
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    limpiar_contenido_tribunal_ambiental() 
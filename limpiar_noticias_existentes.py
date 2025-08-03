#!/usr/bin/env python3
"""
Script para limpiar noticias existentes que contengan texto problemático del Tribunal Ambiental
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

def limpiar_noticias_existentes():
    """Limpiar noticias existentes que contengan texto problemático"""
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("🧹 LIMPIANDO NOTICIAS EXISTENTES")
    print("=" * 50)
    
    # Patrones de texto problemático a eliminar
    patrones_problematicos = [
        r'Acceder al expediente de la causa[A-Z0-9\-]+.*?contacto@tribunalambiental\.cl\.',
        r'Acceder al expediente[A-Z0-9\-]+.*?contacto@tribunalambiental\.cl\.',
        r'Morandé 360, Piso 8, Santiago.*?contacto@tribunalambiental\.cl\.',
        r'Piso 8, Santiago\([0-9\s\+]+\)contacto@tribunalambiental\.cl\.',
        r'\([0-9\s\+]+\)contacto@tribunalambiental\.cl\.',
        r'contacto@tribunalambiental\.cl\.',
        r'R-[0-9\-]+ Morandé 360, Piso 8, Santiago',
        r'Piso 8, Santiago\([0-9\s\+]+\), Piso 8, Santiago',
        r'Acceder al expediente de la causaR-[0-9\-]+ Morandé 360, Piso 8, Santiago\([0-9\s\+]+\), Piso 8, Santiago\([0-9\s\+]+\)contacto@tribunalambiental\.cl\.'
    ]
    
    # Obtener todas las noticias
    print("📊 Obteniendo noticias...")
    response = requests.get(
        f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&order=fecha_publicacion.desc',
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Error obteniendo noticias: {response.status_code}")
        return
    
    noticias = response.json()
    print(f"📋 Total de noticias: {len(noticias)}")
    
    noticias_limpiadas = 0
    noticias_con_problemas = 0
    
    for i, noticia in enumerate(noticias, 1):
        if i % 50 == 0:
            print(f"📝 Procesando noticia {i}/{len(noticias)}")
        
        titulo = noticia.get('titulo', '')
        contenido = noticia.get('cuerpo_completo', '')
        id_noticia = noticia.get('id')
        
        contenido_original = contenido
        contenido_limpio = contenido
        
        # Aplicar cada patrón de limpieza
        for patron in patrones_problematicos:
            contenido_limpio = re.sub(patron, '', contenido_limpio, flags=re.IGNORECASE | re.DOTALL)
        
        # Limpiar espacios múltiples
        contenido_limpio = re.sub(r'\s+', ' ', contenido_limpio)
        contenido_limpio = contenido_limpio.strip()
        
        # Si el contenido cambió, actualizar la noticia
        if contenido_limpio != contenido_original:
            noticias_con_problemas += 1
            print(f"   🧹 Limpiando noticia {i}: {titulo[:50]}...")
            
            # Actualizar la noticia en Supabase
            update_data = {
                'cuerpo_completo': contenido_limpio
            }
            
            update_response = requests.patch(
                f'{SUPABASE_URL}/rest/v1/noticias_juridicas?id=eq.{id_noticia}',
                headers=headers,
                json=update_data
            )
            
            if update_response.status_code == 200:
                noticias_limpiadas += 1
                print(f"      ✅ Actualizada correctamente")
            else:
                print(f"      ❌ Error actualizando: {update_response.status_code}")
    
    print(f"\n📊 RESUMEN FINAL:")
    print(f"📈 Total de noticias procesadas: {len(noticias)}")
    print(f"🧹 Noticias con problemas encontradas: {noticias_con_problemas}")
    print(f"✅ Noticias limpiadas exitosamente: {noticias_limpiadas}")
    
    if noticias_limpiadas > 0:
        print(f"\n🎉 ¡Limpieza completada! Se limpiaron {noticias_limpiadas} noticias.")
    else:
        print(f"\n✅ No se encontraron noticias con texto problemático.")

def verificar_limpieza():
    """Verificar que la limpieza fue exitosa"""
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("\n🔍 VERIFICANDO LIMPIEZA")
    print("=" * 30)
    
    # Buscar noticias que aún contengan texto problemático
    response = requests.get(
        f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&or=(cuerpo_completo.ilike.%Acceder al expediente%,cuerpo_completo.ilike.%Morandé 360%,cuerpo_completo.ilike.%contacto@tribunalambiental%)&limit=10',
        headers=headers
    )
    
    if response.status_code == 200:
        noticias_problematicas = response.json()
        if noticias_problematicas:
            print(f"⚠️  Se encontraron {len(noticias_problematicas)} noticias que aún contienen texto problemático:")
            for noticia in noticias_problematicas:
                print(f"   - {noticia['titulo'][:50]}...")
        else:
            print("✅ No se encontraron noticias con texto problemático.")
    else:
        print(f"❌ Error en verificación: {response.status_code}")

if __name__ == "__main__":
    limpiar_noticias_existentes()
    verificar_limpieza() 
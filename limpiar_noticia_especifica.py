#!/usr/bin/env python3
"""
Script para limpiar la noticia específica que contiene texto problemático
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

def limpiar_noticia_especifica():
    """Limpiar la noticia específica con texto problemático"""
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("🧹 LIMPIANDO NOTICIA ESPECÍFICA")
    print("=" * 50)
    
    # ID de la noticia problemática encontrada
    noticia_id = "cfe80dc3-2457-4f34-a1e7-2b3c81ab474a"
    
    print(f"🎯 Limpiando noticia ID: {noticia_id}")
    
    # Obtener la noticia específica
    response = requests.get(
        f'{SUPABASE_URL}/rest/v1/noticias_juridicas?id=eq.{noticia_id}',
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Error obteniendo noticia: {response.status_code}")
        return
    
    noticias = response.json()
    
    if not noticias:
        print("❌ No se encontró la noticia")
        return
    
    noticia = noticias[0]
    titulo = noticia.get('titulo', '')
    contenido = noticia.get('cuerpo_completo', '')
    fuente = noticia.get('fuente', '')
    
    print(f"📋 Noticia encontrada:")
    print(f"   Título: {titulo}")
    print(f"   Fuente: {fuente}")
    print(f"   Contenido (últimos 200 chars): {contenido[-200:]}")
    
    # Verificar si contiene texto problemático
    tiene_problema = any([
        'Acceder al expediente' in contenido,
        'Morandé 360' in contenido,
        'contacto@tribunalambiental.cl' in contenido
    ])
    
    if not tiene_problema:
        print("✅ La noticia no contiene texto problemático")
        return
    
    print(f"\n⚠️  La noticia contiene texto problemático")
    
    # Limpiar el contenido
    contenido_original = contenido
    contenido_limpio = contenido
    
    # Patrones de limpieza específicos
    patrones_limpiar = [
        r'Acceder al expediente de la causaR-[0-9\-]+ Morandé 360, Piso 8, Santiago\([0-9\s\+]+\), Piso 8, Santiago\([0-9\s\+]+\)contacto@tribunalambiental\.cl\.',
        r'Acceder al expedienteR-[0-9\-]+ Morandé 360, Piso 8, Santiago\([0-9\s\+]+\), Piso 8, Santiago\([0-9\s\+]+\)contacto@tribunalambiental\.cl\.',
        r'Acceder al expediente.*?contacto@tribunalambiental\.cl\.',
        r'Morandé 360, Piso 8, Santiago.*?contacto@tribunalambiental\.cl\.',
        r'Piso 8, Santiago\([0-9\s\+]+\)contacto@tribunalambiental\.cl\.',
        r'\([0-9\s\+]+\)contacto@tribunalambiental\.cl\.',
        r'contacto@tribunalambiental\.cl\.',
        r'Acceder al expediente de la causaR-[0-9\-]+',
        r'Acceder al expedienteR-[0-9\-]+',
        r'Morandé 360, Piso 8, Santiago',
        r'Piso 8, Santiago\([0-9\s\+]+\)',
        r'\([0-9\s\+]+\), Piso 8, Santiago',
    ]
    
    for patron in patrones_limpiar:
        contenido_limpio = re.sub(patron, '', contenido_limpio, flags=re.IGNORECASE | re.DOTALL)
    
    # Limpiar espacios múltiples
    contenido_limpio = re.sub(r'\s+', ' ', contenido_limpio)
    contenido_limpio = contenido_limpio.strip()
    
    print(f"\n🧹 Contenido original (últimos 200 chars):")
    print(f"   {contenido_original[-200:]}")
    
    print(f"\n🧹 Contenido limpio (últimos 200 chars):")
    print(f"   {contenido_limpio[-200:]}")
    
    # Verificar si cambió
    if contenido_limpio != contenido_original:
        print(f"\n✅ Contenido modificado, actualizando en base de datos...")
        
        # Actualizar la noticia
        update_data = {
            'cuerpo_completo': contenido_limpio
        }
        
        update_response = requests.patch(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?id=eq.{noticia_id}',
            headers=headers,
            json=update_data
        )
        
        if update_response.status_code in [200, 204]:
            print(f"✅ Noticia actualizada exitosamente")
            
            # Verificar que se actualizó correctamente
            verify_response = requests.get(
                f'{SUPABASE_URL}/rest/v1/noticias_juridicas?id=eq.{noticia_id}',
                headers=headers
            )
            
            if verify_response.status_code == 200:
                noticia_actualizada = verify_response.json()[0]
                contenido_verificado = noticia_actualizada.get('cuerpo_completo', '')
                
                # Verificar que ya no tiene texto problemático
                tiene_problema_verificado = any([
                    'Acceder al expediente' in contenido_verificado,
                    'Morandé 360' in contenido_verificado,
                    'contacto@tribunalambiental.cl' in contenido_verificado
                ])
                
                if not tiene_problema_verificado:
                    print(f"✅ Verificación exitosa: La noticia ya no contiene texto problemático")
                else:
                    print(f"⚠️  La noticia aún contiene texto problemático")
            else:
                print(f"❌ Error verificando actualización: {verify_response.status_code}")
        else:
            print(f"❌ Error actualizando noticia: {update_response.status_code}")
    else:
        print(f"⚠️  No se detectaron cambios en el contenido")

def verificar_otras_noticias():
    """Verificar si hay otras noticias con texto problemático"""
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    print(f"\n🔍 VERIFICANDO OTRAS NOTICIAS")
    print("=" * 40)
    
    # Obtener más noticias para verificar
    response = requests.get(
        f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&order=fecha_publicacion.desc&limit=20',
        headers=headers
    )
    
    if response.status_code == 200:
        noticias = response.json()
        noticias_con_problemas = []
        
        for noticia in noticias:
            contenido = noticia.get('cuerpo_completo', '')
            if any([
                'Acceder al expediente' in contenido,
                'Morandé 360' in contenido,
                'contacto@tribunalambiental.cl' in contenido
            ]):
                noticias_con_problemas.append(noticia)
        
        if noticias_con_problemas:
            print(f"⚠️  Se encontraron {len(noticias_con_problemas)} noticias con texto problemático:")
            for noticia in noticias_con_problemas:
                print(f"   - ID: {noticia.get('id')} - {noticia.get('titulo', '')[:50]}...")
        else:
            print(f"✅ No se encontraron más noticias con texto problemático")

if __name__ == "__main__":
    limpiar_noticia_especifica()
    verificar_otras_noticias() 
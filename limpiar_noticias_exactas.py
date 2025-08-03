#!/usr/bin/env python3
"""
Script específico para limpiar las 3 noticias exactas con texto problemático
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

def limpiar_noticias_exactas():
    """Limpiar las 3 noticias específicas con texto problemático"""
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("🧹 LIMPIANDO NOTICIAS EXACTAS CON TEXTO PROBLEMÁTICO")
    print("=" * 60)
    
    # Las 3 noticias específicas con texto problemático
    noticias_problematicas = [
        {
            'id': 'cfe80dc3-2457-4f34-a1e7-2b3c81ab474a',
            'texto_problematico': 'Acceder al expediente de la causaR-498-2025 Morandé 360, Piso 8, Santiago(56) 2 2393 69 00, Piso 8, Santiago(56) 2 2393 69 00contacto@tribunalambiental.cl.'
        },
        {
            'id': '96fcb1e0-2f11-4648-9b54-a2913be0c059',
            'texto_problematico': 'Acceder al expediente de la causaR-518-2025 Morandé 360, Piso 8, Santiago(56) 2 2393 69 00, Piso 8, Santiago(56) 2 2393 69 00contacto@tribunalambiental.cl.'
        },
        {
            'id': 'dbec260c-fd07-4294-800c-d47e16c7cf36',
            'texto_problematico': 'Acceder al expedienteR-520-2025 Morandé 360, Piso 8, Santiago(56) 2 2393 69 00, Piso 8, Santiago(56) 2 2393 69 00contacto@tribunalambiental.cl.'
        }
    ]
    
    noticias_limpiadas = 0
    
    for i, noticia_info in enumerate(noticias_problematicas, 1):
        noticia_id = noticia_info['id']
        texto_problematico = noticia_info['texto_problematico']
        
        print(f"\n🧹 Limpiando noticia {i}/3 (ID: {noticia_id})")
        print(f"   Texto problemático: {texto_problematico[:50]}...")
        
        # Obtener la noticia
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?id=eq.{noticia_id}',
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"   ❌ Error obteniendo noticia: {response.status_code}")
            continue
        
        noticias = response.json()
        if not noticias:
            print(f"   ❌ No se encontró la noticia")
            continue
        
        noticia = noticias[0]
        titulo = noticia.get('titulo', '')
        contenido = noticia.get('cuerpo_completo', '')
        
        print(f"   Título: {titulo[:50]}...")
        
        # Verificar si contiene el texto problemático exacto
        if texto_problematico in contenido:
            print(f"   ✅ Texto problemático encontrado en contenido")
            
            # Limpiar el contenido
            contenido_limpio = contenido.replace(texto_problematico, '')
            
            # Limpiar espacios múltiples
            contenido_limpio = re.sub(r'\s+', ' ', contenido_limpio)
            contenido_limpio = contenido_limpio.strip()
            
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
                noticias_limpiadas += 1
                print(f"   ✅ Noticia actualizada exitosamente")
                
                # Verificar que se limpió correctamente
                verify_response = requests.get(
                    f'{SUPABASE_URL}/rest/v1/noticias_juridicas?id=eq.{noticia_id}',
                    headers=headers
                )
                
                if verify_response.status_code == 200:
                    noticia_verificada = verify_response.json()[0]
                    contenido_verificado = noticia_verificada.get('cuerpo_completo', '')
                    
                    if texto_problematico not in contenido_verificado:
                        print(f"   ✅ Verificación exitosa: Texto problemático eliminado")
                    else:
                        print(f"   ⚠️  El texto problemático aún está presente")
                else:
                    print(f"   ❌ Error verificando: {verify_response.status_code}")
            else:
                print(f"   ❌ Error actualizando: {update_response.status_code}")
        else:
            print(f"   ⚠️  Texto problemático no encontrado en contenido")
            
            # Buscar en otros campos
            resumen = noticia.get('resumen_ejecutivo', '')
            extracto = noticia.get('extracto_fuente', '')
            
            if texto_problematico in resumen:
                print(f"   ✅ Texto problemático encontrado en resumen_ejecutivo")
                resumen_limpio = resumen.replace(texto_problematico, '')
                resumen_limpio = re.sub(r'\s+', ' ', resumen_limpio).strip()
                
                update_data = {
                    'resumen_ejecutivo': resumen_limpio
                }
                
                update_response = requests.patch(
                    f'{SUPABASE_URL}/rest/v1/noticias_juridicas?id=eq.{noticia_id}',
                    headers=headers,
                    json=update_data
                )
                
                if update_response.status_code in [200, 204]:
                    noticias_limpiadas += 1
                    print(f"   ✅ Resumen actualizado exitosamente")
                else:
                    print(f"   ❌ Error actualizando resumen: {update_response.status_code}")
            
            elif texto_problematico in extracto:
                print(f"   ✅ Texto problemático encontrado en extracto_fuente")
                extracto_limpio = extracto.replace(texto_problematico, '')
                extracto_limpio = re.sub(r'\s+', ' ', extracto_limpio).strip()
                
                update_data = {
                    'extracto_fuente': extracto_limpio
                }
                
                update_response = requests.patch(
                    f'{SUPABASE_URL}/rest/v1/noticias_juridicas?id=eq.{noticia_id}',
                    headers=headers,
                    json=update_data
                )
                
                if update_response.status_code in [200, 204]:
                    noticias_limpiadas += 1
                    print(f"   ✅ Extracto actualizado exitosamente")
                else:
                    print(f"   ❌ Error actualizando extracto: {update_response.status_code}")
    
    print(f"\n📊 RESUMEN FINAL:")
    print(f"📈 Total de noticias procesadas: {len(noticias_problematicas)}")
    print(f"🧹 Noticias limpiadas exitosamente: {noticias_limpiadas}")
    
    if noticias_limpiadas > 0:
        print(f"\n🎉 ¡Limpieza completada! Se limpiaron {noticias_limpiadas} noticias.")
        print("🔄 Recarga el frontend para ver los cambios.")
    else:
        print(f"\n⚠️  No se pudieron limpiar las noticias.")

def verificar_limpieza():
    """Verificar que la limpieza fue exitosa"""
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    print(f"\n🔍 VERIFICANDO LIMPIEZA")
    print("=" * 30)
    
    # IDs de las noticias que se limpiaron
    ids_noticias = [
        'cfe80dc3-2457-4f34-a1e7-2b3c81ab474a',
        '96fcb1e0-2f11-4648-9b54-a2913be0c059',
        'dbec260c-fd07-4294-800c-d47e16c7cf36'
    ]
    
    for noticia_id in ids_noticias:
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?id=eq.{noticia_id}',
            headers=headers
        )
        
        if response.status_code == 200:
            noticias = response.json()
            if noticias:
                noticia = noticias[0]
                contenido = noticia.get('cuerpo_completo', '')
                resumen = noticia.get('resumen_ejecutivo', '')
                extracto = noticia.get('extracto_fuente', '')
                
                # Verificar si aún contiene texto problemático
                tiene_problema = any([
                    'Acceder al expediente' in contenido,
                    'Morandé 360' in contenido,
                    'contacto@tribunalambiental.cl' in contenido,
                    'Acceder al expediente' in resumen,
                    'Morandé 360' in resumen,
                    'contacto@tribunalambiental.cl' in resumen,
                    'Acceder al expediente' in extracto,
                    'Morandé 360' in extracto,
                    'contacto@tribunalambiental.cl' in extracto
                ])
                
                if tiene_problema:
                    print(f"   ⚠️  Noticia {noticia_id}: AÚN TIENE TEXTO PROBLEMÁTICO")
                else:
                    print(f"   ✅ Noticia {noticia_id}: LIMPIA")
            else:
                print(f"   ❌ Noticia {noticia_id}: No encontrada")
        else:
            print(f"   ❌ Error verificando noticia {noticia_id}: {response.status_code}")

if __name__ == "__main__":
    limpiar_noticias_exactas()
    verificar_limpieza() 
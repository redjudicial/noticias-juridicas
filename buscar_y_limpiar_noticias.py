#!/usr/bin/env python3
"""
Script directo para buscar y limpiar noticias con texto problemático específico
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

def buscar_y_limpiar_noticias():
    """Buscar y limpiar noticias con texto problemático"""
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 BUSCANDO Y LIMPIANDO NOTICIAS CON TEXTO PROBLEMÁTICO")
    print("=" * 60)
    
    # Obtener todas las noticias recientes
    print("📊 Obteniendo noticias recientes...")
    response = requests.get(
        f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&order=fecha_publicacion.desc&limit=50',
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Error obteniendo noticias: {response.status_code}")
        return
    
    noticias = response.json()
    print(f"📋 Total de noticias obtenidas: {len(noticias)}")
    
    # Textos problemáticos específicos
    textos_problematicos = [
        "Acceder al expediente de la causaR-498-2025",
        "Acceder al expediente de la causaR-518-2025", 
        "Acceder al expedienteR-520-2025",
        "Morandé 360, Piso 8, Santiago",
        "contacto@tribunalambiental.cl"
    ]
    
    noticias_con_problemas = []
    
    # Buscar noticias con texto problemático
    for noticia in noticias:
        titulo = noticia.get('titulo', '')
        contenido = noticia.get('cuerpo_completo', '')
        texto_completo = f"{titulo} {contenido}"
        
        # Verificar si contiene texto problemático
        tiene_problema = False
        for texto_problematico in textos_problematicos:
            if texto_problematico in texto_completo:
                tiene_problema = True
                break
        
        if tiene_problema:
            noticias_con_problemas.append(noticia)
            print(f"⚠️  Noticia con problema encontrada:")
            print(f"   ID: {noticia.get('id')}")
            print(f"   Título: {titulo[:50]}...")
            print(f"   Fuente: {noticia.get('fuente', '')}")
            print(f"   Contenido (últimos 100 chars): {contenido[-100:]}")
            print()
    
    print(f"📊 Noticias con problemas encontradas: {len(noticias_con_problemas)}")
    
    if not noticias_con_problemas:
        print("✅ No se encontraron noticias con texto problemático")
        return
    
    # Limpiar noticias encontradas
    noticias_limpiadas = 0
    
    for i, noticia in enumerate(noticias_con_problemas, 1):
        id_noticia = noticia.get('id')
        contenido = noticia.get('cuerpo_completo', '')
        
        print(f"🧹 Limpiando noticia {i}/{len(noticias_con_problemas)} (ID: {id_noticia})")
        
        contenido_original = contenido
        contenido_limpio = contenido
        
        # Eliminar texto problemático específico
        patrones_limpiar = [
            r'Acceder al expediente de la causaR-[0-9\-]+ Morandé 360, Piso 8, Santiago\([0-9\s\+]+\), Piso 8, Santiago\([0-9\s\+]+\)contacto@tribunalambiental\.cl\.',
            r'Acceder al expedienteR-[0-9\-]+ Morandé 360, Piso 8, Santiago\([0-9\s\+]+\), Piso 8, Santiago\([0-9\s\+]+\)contacto@tribunalambiental\.cl\.',
            r'Acceder al expediente.*?contacto@tribunalambiental\.cl\.',
            r'Morandé 360, Piso 8, Santiago.*?contacto@tribunalambiental\.cl\.',
            r'Piso 8, Santiago\([0-9\s\+]+\)contacto@tribunalambiental\.cl\.',
            r'\([0-9\s\+]+\)contacto@tribunalambiental\.cl\.',
            r'contacto@tribunalambiental\.cl\.',
        ]
        
        for patron in patrones_limpiar:
            contenido_limpio = re.sub(patron, '', contenido_limpio, flags=re.IGNORECASE | re.DOTALL)
        
        # Limpiar espacios múltiples
        contenido_limpio = re.sub(r'\s+', ' ', contenido_limpio)
        contenido_limpio = contenido_limpio.strip()
        
        # Verificar si cambió
        if contenido_limpio != contenido_original:
            print(f"   ✅ Contenido modificado")
            
            # Actualizar en Supabase
            update_data = {
                'cuerpo_completo': contenido_limpio
            }
            
            update_response = requests.patch(
                f'{SUPABASE_URL}/rest/v1/noticias_juridicas?id=eq.{id_noticia}',
                headers=headers,
                json=update_data
            )
            
            if update_response.status_code in [200, 204]:
                noticias_limpiadas += 1
                print(f"   ✅ Actualizada en base de datos")
            else:
                print(f"   ❌ Error actualizando: {update_response.status_code}")
        else:
            print(f"   ⚠️  No se detectaron cambios")
    
    print(f"\n📊 RESUMEN FINAL:")
    print(f"📈 Total de noticias con problemas: {len(noticias_con_problemas)}")
    print(f"🧹 Noticias limpiadas exitosamente: {noticias_limpiadas}")
    
    if noticias_limpiadas > 0:
        print(f"\n🎉 ¡Limpieza completada! Se limpiaron {noticias_limpiadas} noticias.")
        print("🔄 Recarga el frontend para ver los cambios.")
    else:
        print(f"\n⚠️  No se pudieron limpiar las noticias.")

def verificar_noticias_recientes():
    """Verificar noticias recientes del Tribunal Ambiental"""
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("\n🔍 VERIFICANDO NOTICIAS RECIENTES DEL TRIBUNAL AMBIENTAL")
    print("=" * 60)
    
    # Buscar noticias recientes del Tribunal Ambiental
    fuentes_ambientales = ['tribunal_ambiental', '1ta', '3ta']
    
    for fuente in fuentes_ambientales:
        print(f"\n📋 Verificando {fuente}:")
        
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&fuente=eq.{fuente}&order=fecha_publicacion.desc&limit=5',
            headers=headers
        )
        
        if response.status_code == 200:
            noticias = response.json()
            print(f"   Encontradas {len(noticias)} noticias")
            
            for i, noticia in enumerate(noticias, 1):
                titulo = noticia.get('titulo', '')
                contenido = noticia.get('cuerpo_completo', '')
                
                # Verificar si contiene texto problemático
                tiene_problema = any([
                    'Acceder al expediente' in contenido,
                    'Morandé 360' in contenido,
                    'contacto@tribunalambiental.cl' in contenido
                ])
                
                if tiene_problema:
                    print(f"   ⚠️  Noticia {i}: TIENE TEXTO PROBLEMÁTICO")
                    print(f"      Título: {titulo}")
                    print(f"      Contenido (últimos 100 chars): {contenido[-100:]}")
                else:
                    print(f"   ✅ Noticia {i}: Sin problemas")
        else:
            print(f"   ❌ Error: {response.status_code}")

if __name__ == "__main__":
    buscar_y_limpiar_noticias()
    verificar_noticias_recientes() 
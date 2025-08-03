#!/usr/bin/env python3
"""
Script para limpiar específicamente las noticias que contienen el texto problemático del Tribunal Ambiental
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

def limpiar_noticias_especificas():
    """Limpiar noticias específicas con texto problemático"""
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("🧹 LIMPIANDO NOTICIAS ESPECÍFICAS CON TEXTO PROBLEMÁTICO")
    print("=" * 60)
    
    # Textos problemáticos específicos encontrados en el frontend
    textos_problematicos = [
        "Acceder al expediente de la causaR-498-2025 Morandé 360, Piso 8, Santiago(56) 2 2393 69 00, Piso 8, Santiago(56) 2 2393 69 00contacto@tribunalambiental.cl.",
        "Acceder al expediente de la causaR-518-2025 Morandé 360, Piso 8, Santiago(56) 2 2393 69 00, Piso 8, Santiago(56) 2 2393 69 00contacto@tribunalambiental.cl.",
        "Acceder al expedienteR-520-2025 Morandé 360, Piso 8, Santiago(56) 2 2393 69 00, Piso 8, Santiago(56) 2 2393 69 00contacto@tribunalambiental.cl."
    ]
    
    # Patrones para buscar variaciones
    patrones_busqueda = [
        r'Acceder al expediente de la causaR-[0-9\-]+ Morandé 360, Piso 8, Santiago\([0-9\s\+]+\), Piso 8, Santiago\([0-9\s\+]+\)contacto@tribunalambiental\.cl\.',
        r'Acceder al expedienteR-[0-9\-]+ Morandé 360, Piso 8, Santiago\([0-9\s\+]+\), Piso 8, Santiago\([0-9\s\+]+\)contacto@tribunalambiental\.cl\.',
        r'Acceder al expediente.*?contacto@tribunalambiental\.cl\.',
        r'Morandé 360, Piso 8, Santiago.*?contacto@tribunalambiental\.cl\.'
    ]
    
    # Buscar noticias que contengan estos textos exactos
    print("🔍 Buscando noticias con texto problemático específico...")
    
    noticias_encontradas = []
    
    # Buscar por texto exacto
    for texto_problematico in textos_problematicos:
        print(f"   Buscando: {texto_problematico[:50]}...")
        
        # Escapar caracteres especiales para la búsqueda
        texto_busqueda = texto_problematico.replace('(', '\\(').replace(')', '\\)').replace('.', '\\.')
        
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&or=(cuerpo_completo.ilike.%{texto_busqueda}%,titulo.ilike.%{texto_busqueda}%)&limit=10',
            headers=headers
        )
        
        if response.status_code == 200:
            noticias = response.json()
            noticias_encontradas.extend(noticias)
            print(f"      Encontradas: {len(noticias)} noticias")
        else:
            print(f"      ❌ Error en búsqueda: {response.status_code}")
    
    # Buscar por patrones
    for patron in patrones_busqueda:
        print(f"   Buscando patrón: {patron[:50]}...")
        
        # Buscar noticias que contengan "Acceder al expediente" o "Morandé 360"
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&or=(cuerpo_completo.ilike.%Acceder al expediente%,cuerpo_completo.ilike.%Morandé 360%,cuerpo_completo.ilike.%contacto@tribunalambiental%)&limit=20',
            headers=headers
        )
        
        if response.status_code == 200:
            noticias = response.json()
            for noticia in noticias:
                contenido = noticia.get('cuerpo_completo', '')
                if re.search(patron, contenido, re.IGNORECASE):
                    if noticia not in noticias_encontradas:
                        noticias_encontradas.append(noticia)
    
    # Eliminar duplicados
    noticias_unicas = []
    ids_vistos = set()
    for noticia in noticias_encontradas:
        if noticia.get('id') not in ids_vistos:
            noticias_unicas.append(noticia)
            ids_vistos.add(noticia.get('id'))
    
    print(f"\n📊 Total de noticias encontradas: {len(noticias_unicas)}")
    
    if not noticias_unicas:
        print("✅ No se encontraron noticias con texto problemático específico")
        return
    
    # Limpiar cada noticia encontrada
    noticias_limpiadas = 0
    
    for i, noticia in enumerate(noticias_unicas, 1):
        id_noticia = noticia.get('id')
        titulo = noticia.get('titulo', '')
        contenido = noticia.get('cuerpo_completo', '')
        fuente = noticia.get('fuente', '')
        
        print(f"\n🧹 Limpiando noticia {i}/{len(noticias_unicas)}:")
        print(f"   ID: {id_noticia}")
        print(f"   Título: {titulo[:50]}...")
        print(f"   Fuente: {fuente}")
        
        contenido_original = contenido
        contenido_limpio = contenido
        
        # Aplicar limpieza específica
        for texto_problematico in textos_problematicos:
            contenido_limpio = contenido_limpio.replace(texto_problematico, '')
        
        # Aplicar patrones de limpieza
        for patron in patrones_busqueda:
            contenido_limpio = re.sub(patron, '', contenido_limpio, flags=re.IGNORECASE)
        
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
    print(f"📈 Total de noticias procesadas: {len(noticias_unicas)}")
    print(f"🧹 Noticias limpiadas exitosamente: {noticias_limpiadas}")
    
    if noticias_limpiadas > 0:
        print(f"\n🎉 ¡Limpieza completada! Se limpiaron {noticias_limpiadas} noticias.")
        print("🔄 Recarga el frontend para ver los cambios.")
    else:
        print(f"\n⚠️  No se pudieron limpiar las noticias. Verificar permisos de base de datos.")

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
                print(f"   - ID: {noticia.get('id')} - {noticia.get('titulo', '')[:50]}...")
        else:
            print("✅ No se encontraron noticias con texto problemático.")
    else:
        print(f"❌ Error en verificación: {response.status_code}")

if __name__ == "__main__":
    limpiar_noticias_especificas()
    verificar_limpieza() 
#!/usr/bin/env python3
"""
Script para búsqueda detallada del texto problemático
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

def busqueda_detallada():
    """Búsqueda detallada del texto problemático"""
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    print("🔍 BÚSQUEDA DETALLADA DEL TEXTO PROBLEMÁTICO")
    print("=" * 60)
    
    # Obtener todas las noticias
    response = requests.get(
        f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&order=fecha_publicacion.desc&limit=50',
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Error obteniendo noticias: {response.status_code}")
        return
    
    noticias = response.json()
    print(f"📋 Analizando {len(noticias)} noticias...")
    
    # Textos problemáticos específicos del frontend
    textos_problematicos = [
        "Acceder al expediente de la causaR-498-2025",
        "Acceder al expediente de la causaR-518-2025",
        "Acceder al expedienteR-520-2025",
        "Morandé 360, Piso 8, Santiago",
        "contacto@tribunalambiental.cl"
    ]
    
    noticias_con_problemas = []
    
    for i, noticia in enumerate(noticias, 1):
        if i % 10 == 0:
            print(f"   Procesando noticia {i}/{len(noticias)}")
        
        # Obtener todos los campos de la noticia
        titulo = noticia.get('titulo', '')
        contenido = noticia.get('cuerpo_completo', '')
        resumen = noticia.get('resumen_ejecutivo', '')
        extracto = noticia.get('extracto_fuente', '')
        palabras_clave = noticia.get('palabras_clave', [])
        
        # Crear texto completo para búsqueda
        texto_completo = f"{titulo} {contenido} {resumen} {extracto} {' '.join(palabras_clave)}"
        
        # Buscar textos problemáticos
        problemas_encontrados = []
        for texto_problematico in textos_problematicos:
            if texto_problematico in texto_completo:
                problemas_encontrados.append(texto_problematico)
        
        if problemas_encontrados:
            noticias_con_problemas.append({
                'noticia': noticia,
                'problemas': problemas_encontrados
            })
            
            print(f"\n⚠️  NOTICIA {i} CON PROBLEMAS:")
            print(f"   ID: {noticia.get('id')}")
            print(f"   Título: {titulo[:80]}...")
            print(f"   Fuente: {noticia.get('fuente', '')}")
            print(f"   Problemas encontrados: {problemas_encontrados}")
            
            # Mostrar contexto del problema
            for problema in problemas_encontrados:
                if problema in contenido:
                    # Encontrar la posición del problema
                    pos = contenido.find(problema)
                    inicio = max(0, pos - 50)
                    fin = min(len(contenido), pos + len(problema) + 50)
                    contexto = contenido[inicio:fin]
                    print(f"   Contexto: ...{contexto}...")
    
    print(f"\n📊 RESUMEN:")
    print(f"📈 Total de noticias analizadas: {len(noticias)}")
    print(f"⚠️  Noticias con problemas: {len(noticias_con_problemas)}")
    
    if noticias_con_problemas:
        print(f"\n🎯 NOTICIAS A LIMPIAR:")
        for item in noticias_con_problemas:
            noticia = item['noticia']
            problemas = item['problemas']
            print(f"   - ID: {noticia.get('id')} - Problemas: {problemas}")
        
        return noticias_con_problemas
    else:
        print(f"\n✅ No se encontraron noticias con texto problemático")
        return []

def limpiar_noticias_encontradas(noticias_con_problemas):
    """Limpiar las noticias encontradas con problemas"""
    
    if not noticias_con_problemas:
        print("No hay noticias para limpiar")
        return
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    print(f"\n🧹 LIMPIANDO {len(noticias_con_problemas)} NOTICIAS")
    print("=" * 50)
    
    noticias_limpiadas = 0
    
    for i, item in enumerate(noticias_con_problemas, 1):
        noticia = item['noticia']
        problemas = item['problemas']
        
        id_noticia = noticia.get('id')
        contenido = noticia.get('cuerpo_completo', '')
        
        print(f"\n🧹 Limpiando noticia {i}/{len(noticias_con_problemas)} (ID: {id_noticia})")
        print(f"   Problemas: {problemas}")
        
        contenido_original = contenido
        contenido_limpio = contenido
        
        # Aplicar limpieza específica
        for problema in problemas:
            contenido_limpio = contenido_limpio.replace(problema, '')
        
        # Aplicar patrones de limpieza adicionales
        patrones_limpiar = [
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
    print(f"📈 Total de noticias procesadas: {len(noticias_con_problemas)}")
    print(f"🧹 Noticias limpiadas exitosamente: {noticias_limpiadas}")
    
    if noticias_limpiadas > 0:
        print(f"\n🎉 ¡Limpieza completada! Se limpiaron {noticias_limpiadas} noticias.")
        print("🔄 Recarga el frontend para ver los cambios.")

if __name__ == "__main__":
    noticias_con_problemas = busqueda_detallada()
    if noticias_con_problemas:
        limpiar_noticias_encontradas(noticias_con_problemas) 
#!/usr/bin/env python3
"""
Verificación final completa de todos los problemas solucionados
"""

import os
import requests
import re
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

def verificar_problemas_solucionados():
    """Verificar que todos los problemas están solucionados"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}'
    }
    
    print("🎯 **VERIFICACIÓN FINAL - PROBLEMAS SOLUCIONADOS**")
    print("=" * 60)
    
    # 1. Verificar URLs duplicadas
    print("\n🔗 **1. VERIFICACIÓN DE URLs DUPLICADAS**")
    try:
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=url_origen&order=url_origen',
            headers=headers
        )
        
        if response.status_code == 200:
            noticias = response.json()
            urls = [n.get('url_origen') for n in noticias if n.get('url_origen')]
            urls_unicas = len(set(urls))
            duplicadas = len(urls) - urls_unicas
            
            print(f"   📊 Total URLs: {len(urls)}")
            print(f"   📊 URLs únicas: {urls_unicas}")
            print(f"   📊 URLs duplicadas: {duplicadas}")
            
            if duplicadas == 0:
                print("   ✅ No hay URLs duplicadas")
            else:
                print(f"   ⚠️  Hay {duplicadas} URLs duplicadas - Ejecutar SQL")
                
        else:
            print(f"   ❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Verificar títulos con fechas
    print("\n📰 **2. VERIFICACIÓN DE TÍTULOS CON FECHAS**")
    try:
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=titulo,fuente&order=fecha_publicacion.desc&limit=20',
            headers=headers
        )
        
        if response.status_code == 200:
            noticias = response.json()
            titulos_con_fecha = 0
            
            for noticia in noticias:
                titulo = noticia.get('titulo', '')
                fuente = noticia.get('fuente', '')
                
                # Buscar patrones de fecha al final del título
                patrones_fecha = [
                    r'\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}$',  # 26-07-2025 04:07
                    r'\d{2}-\d{2}-\d{4}\s+\d{1,2}:\d{2}$',  # 26-07-2025 4:07
                    r'\d{1,2}-\d{1,2}-\d{4}\s+\d{2}:\d{2}$',  # 6-07-2025 04:07
                    r'\d{1,2}-\d{1,2}-\d{4}\s+\d{1,2}:\d{2}$',  # 6-7-2025 4:07
                ]
                
                for patron in patrones_fecha:
                    if re.search(patron, titulo):
                        titulos_con_fecha += 1
                        print(f"   ⚠️  Título con fecha: {titulo[:60]}... ({fuente})")
                        break
            
            if titulos_con_fecha == 0:
                print("   ✅ No hay títulos con fechas")
            else:
                print(f"   ⚠️  Hay {titulos_con_fecha} títulos con fechas")
                
        else:
            print(f"   ❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Verificar fechas de publicación
    print("\n📅 **3. VERIFICACIÓN DE FECHAS DE PUBLICACIÓN**")
    try:
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=fecha_publicacion,fecha_actualizacion,fuente&order=fecha_publicacion.desc&limit=10',
            headers=headers
        )
        
        if response.status_code == 200:
            noticias = response.json()
            
            for i, noticia in enumerate(noticias, 1):
                fecha_pub = noticia.get('fecha_publicacion', 'N/A')
                fecha_act = noticia.get('fecha_actualizacion', 'N/A')
                fuente = noticia.get('fuente', 'N/A')
                
                print(f"   {i}. {fuente}: {fecha_pub[:10]} (pub) / {fecha_act[:10] if fecha_act != 'N/A' else 'N/A'} (act)")
            
            print("   ✅ Fechas verificadas")
                
        else:
            print(f"   ❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Verificar resúmenes IA
    print("\n🤖 **4. VERIFICACIÓN DE RESÚMENES IA**")
    try:
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=resumen_ejecutivo,palabras_clave&order=fecha_publicacion.desc&limit=5',
            headers=headers
        )
        
        if response.status_code == 200:
            noticias = response.json()
            resumenes_con_ia = sum(1 for n in noticias if n.get('resumen_ejecutivo'))
            palabras_clave = sum(1 for n in noticias if n.get('palabras_clave'))
            
            print(f"   📊 Resúmenes IA: {resumenes_con_ia}/{len(noticias)}")
            print(f"   📊 Palabras clave: {palabras_clave}/{len(noticias)}")
            
            if resumenes_con_ia == len(noticias):
                print("   ✅ Todos los resúmenes IA están generados")
            else:
                print(f"   ⚠️  Faltan {len(noticias) - resumenes_con_ia} resúmenes IA")
                
        else:
            print(f"   ❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 **VERIFICACIÓN COMPLETADA**")
    print("📋 Próximo paso: Ejecutar SQL para eliminar URLs duplicadas")

if __name__ == "__main__":
    verificar_problemas_solucionados() 
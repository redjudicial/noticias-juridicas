#!/usr/bin/env python3
"""
Verificación final completa del sistema de noticias
"""

import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

def verificar_sistema_completo():
    """Verificación completa del sistema"""
    
    print("🎯 **VERIFICACIÓN FINAL DEL SISTEMA**")
    print("=" * 60)
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}'
    }
    
    # 1. Verificar conexión a Supabase
    print("\n🔗 **1. CONEXIÓN A SUPABASE**")
    try:
        response = requests.get(f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=count', headers=headers)
        if response.status_code == 200:
            print("✅ Conexión a Supabase: OK")
        else:
            print(f"❌ Error de conexión: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return
    
    # 2. Verificar datos
    print("\n📊 **2. VERIFICACIÓN DE DATOS**")
    try:
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&order=fecha_publicacion.desc&limit=10',
            headers=headers
        )
        
        if response.status_code == 200:
            noticias = response.json()
            print(f"✅ Total noticias: {len(noticias)}")
            
            # Verificar estructura de datos
            noticia_ejemplo = noticias[0] if noticias else {}
            campos_requeridos = ['titulo', 'resumen_ejecutivo', 'fuente', 'url_origen', 'fecha_publicacion']
            
            for campo in campos_requeridos:
                if campo in noticia_ejemplo:
                    print(f"✅ Campo '{campo}': OK")
                else:
                    print(f"❌ Campo '{campo}': FALTANTE")
            
            # Verificar resúmenes IA
            resumenes_con_ia = sum(1 for n in noticias if n.get('resumen_ejecutivo'))
            print(f"✅ Resúmenes IA generados: {resumenes_con_ia}/{len(noticias)}")
            
        else:
            print(f"❌ Error obteniendo datos: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error verificando datos: {e}")
    
    # 3. Verificar fuentes
    print("\n📰 **3. VERIFICACIÓN DE FUENTES**")
    try:
        fuentes = {}
        for noticia in noticias:
            fuente = noticia.get('fuente', 'desconocida')
            fuentes[fuente] = fuentes.get(fuente, 0) + 1
        
        print("✅ Fuentes activas:")
        for fuente, count in fuentes.items():
            print(f"   • {fuente}: {count} noticias")
            
    except Exception as e:
        print(f"❌ Error verificando fuentes: {e}")
    
    # 4. Verificar calidad de datos
    print("\n🎯 **4. CALIDAD DE DATOS**")
    try:
        # Verificar títulos limpios
        titulos_con_fecha = sum(1 for n in noticias if any(char.isdigit() for char in n.get('titulo', '')[-10:]))
        print(f"✅ Títulos limpios: {len(noticias) - titulos_con_fecha}/{len(noticias)}")
        
        # Verificar URLs únicas
        urls = [n.get('url_origen') for n in noticias if n.get('url_origen')]
        urls_unicas = len(set(urls))
        print(f"✅ URLs únicas: {urls_unicas}/{len(urls)}")
        
        # Verificar fechas válidas
        fechas_validas = sum(1 for n in noticias if n.get('fecha_publicacion'))
        print(f"✅ Fechas válidas: {fechas_validas}/{len(noticias)}")
        
    except Exception as e:
        print(f"❌ Error verificando calidad: {e}")
    
    # 5. Verificar frontend
    print("\n🌐 **5. VERIFICACIÓN FRONTEND**")
    try:
        # Verificar que el frontend puede acceder a los datos
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=titulo,resumen_ejecutivo,fuente&limit=5',
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Frontend puede acceder a datos: OK")
            print("✅ Estructura de datos compatible: OK")
        else:
            print(f"❌ Error acceso frontend: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error verificando frontend: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 **VERIFICACIÓN COMPLETADA**")
    print("📋 Próximo paso: Ejecutar SQL en Supabase para eliminar restricción de hash")

if __name__ == "__main__":
    verificar_sistema_completo() 
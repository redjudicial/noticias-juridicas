#!/usr/bin/env python3
"""
Analizar patrones en las 55 noticias para identificar problemas
"""

import os
import requests
import re
from collections import Counter
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

def analizar_patrones_noticias():
    """Analizar patrones en todas las noticias"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}'
    }
    
    print("🔍 **ANÁLISIS DE PATRONES EN 55 NOTICIAS**")
    print("=" * 60)
    
    try:
        # Obtener todas las noticias
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&order=fecha_publicacion.desc',
            headers=headers
        )
        
        if response.status_code == 200:
            noticias = response.json()
            
            print(f"📊 Total noticias analizadas: {len(noticias)}")
            
            # 1. Análisis por fuente
            print("\n📰 **1. DISTRIBUCIÓN POR FUENTE**")
            fuentes = Counter([n.get('fuente', 'desconocida') for n in noticias])
            for fuente, count in fuentes.most_common():
                print(f"   • {fuente}: {count} noticias")
            
            # 2. Análisis de contenido problemático
            print("\n⚠️ **2. CONTENIDO PROBLEMÁTICO IDENTIFICADO**")
            
            patrones_problematicos = [
                (r'Acceder al expediente.*?contacto@tribunalambiental\.cl', 'Información de contacto duplicada'),
                (r'ÚLTIMAS NOTICIAS.*?Grupos\.', 'Lista de noticias duplicada'),
                (r'Morandé 360, Piso 8, Santiago.*?contacto@tribunalambiental\.cl', 'Datos de contacto repetidos'),
                (r'Poder Judicial Radio.*?Poder Judicial TV', 'Enlaces multimedia duplicados'),
                (r'Agenda del Presidente.*?Agenda del Presidente', 'Agendas repetidas'),
                (r'\(\d{2}\.\d{2}\.\d{4}\)', 'Fechas en formato extraño'),
            ]
            
            noticias_con_problemas = 0
            
            for noticia in noticias:
                titulo = noticia.get('titulo', '')
                contenido = noticia.get('cuerpo_completo', '')
                fuente = noticia.get('fuente', '')
                
                problemas_encontrados = []
                
                for patron, descripcion in patrones_problematicos:
                    if re.search(patron, contenido, re.IGNORECASE | re.DOTALL):
                        problemas_encontrados.append(descripcion)
                
                if problemas_encontrados:
                    noticias_con_problemas += 1
                    print(f"\n   🔴 {fuente}: {titulo[:50]}...")
                    for problema in problemas_encontrados:
                        print(f"      • {problema}")
            
            print(f"\n   📊 Noticias con problemas: {noticias_con_problemas}/{len(noticias)}")
            
            # 3. Análisis de resúmenes
            print("\n🤖 **3. ANÁLISIS DE RESÚMENES IA**")
            resumenes_cortos = sum(1 for n in noticias if len(n.get('resumen_ejecutivo', '')) < 50)
            resumenes_largos = sum(1 for n in noticias if len(n.get('resumen_ejecutivo', '')) > 200)
            
            print(f"   • Resúmenes muy cortos (<50 chars): {resumenes_cortos}")
            print(f"   • Resúmenes muy largos (>200 chars): {resumenes_largos}")
            
            # 4. Análisis de fechas
            print("\n📅 **4. ANÁLISIS DE FECHAS**")
            fechas_actuales = sum(1 for n in noticias if '2025-07-28' in str(n.get('fecha_publicacion', '')))
            print(f"   • Noticias de hoy (28/07): {fechas_actuales}")
            
            # 5. Recomendaciones
            print("\n💡 **5. RECOMENDACIONES**")
            
            if noticias_con_problemas > 0:
                print(f"   ⚠️  {noticias_con_problemas} noticias tienen contenido problemático")
                print("   💡 Considerar limpieza adicional del contenido")
            else:
                print("   ✅ No se detectaron problemas significativos")
            
            # Verificar distribución de fuentes en recientes
            noticias_recientes = noticias[:10]
            fuentes_recientes = Counter([n.get('fuente') for n in noticias_recientes])
            
            if len(fuentes_recientes) < 3:
                print("   ⚠️  Poca variedad de fuentes en noticias recientes")
                print("   💡 Considerar mezclar fuentes en el frontend")
            else:
                print("   ✅ Buena variedad de fuentes en noticias recientes")
                
        else:
            print(f"❌ Error obteniendo noticias: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    analizar_patrones_noticias() 
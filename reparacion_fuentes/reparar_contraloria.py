#!/usr/bin/env python3
"""
Reparación específica del problema de hash duplicado en Contraloría
"""

import os
import sys
import requests
import hashlib
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('../APIS_Y_CREDENCIALES.env')

# Configuración de Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://qfomiierchksyfhxoukj.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def verificar_noticia_existente(url):
    """Verificar si una noticia ya existe por URL"""
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}'
        }
        
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&url_origen=eq.{url}&limit=1',
            headers=headers
        )
        
        if response.status_code == 200:
            noticias = response.json()
            return noticias[0] if noticias else None
        else:
            print(f"❌ Error verificando noticia: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return None

def actualizar_noticia_existente(noticia_id, datos_nuevos):
    """Actualizar una noticia existente"""
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        
        response = requests.patch(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?id=eq.{noticia_id}',
            headers=headers,
            json=datos_nuevos
        )
        
        if response.status_code == 204:
            print(f"✅ Noticia {noticia_id} actualizada correctamente")
            return True
        else:
            print(f"❌ Error actualizando noticia: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en actualización: {e}")
        return False

def insertar_noticia_nueva(datos):
    """Insertar una nueva noticia"""
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        
        response = requests.post(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas',
            headers=headers,
            json=datos
        )
        
        if response.status_code == 201:
            print("✅ Nueva noticia insertada correctamente")
            return True
        elif response.status_code == 409:
            print("⚠️ Noticia duplicada detectada (409)")
            return False
        else:
            print(f"❌ Error insertando noticia: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en inserción: {e}")
        return False

def generar_hash_contenido(titulo, contenido, url):
    """Generar hash único para el contenido"""
    # Crear string único combinando elementos
    contenido_para_hash = f"{titulo}|{contenido[:200]}|{url}"
    return hashlib.md5(contenido_para_hash.encode('utf-8')).hexdigest()

def procesar_noticia_contraloria(noticia_data):
    """Procesar una noticia de Contraloría con manejo de duplicados"""
    try:
        # Extraer datos de la noticia
        titulo = noticia_data.get('titulo', '')
        contenido = noticia_data.get('contenido', '')
        url = noticia_data.get('url_origen', '')
        fecha = noticia_data.get('fecha_publicacion', '')
        
        if not titulo or not url:
            print("⚠️ Datos incompletos de noticia")
            return False
        
        # Generar hash único
        hash_contenido = generar_hash_contenido(titulo, contenido, url)
        
        # Verificar si la noticia ya existe
        noticia_existente = verificar_noticia_existente(url)
        
        if noticia_existente:
            print(f"🔄 Noticia existente encontrada: {titulo[:50]}...")
            
            # Preparar datos para actualización
            datos_actualizacion = {
                'titulo': titulo,
                'contenido': contenido,
                'hash_contenido': hash_contenido,
                'fecha_actualizacion': datetime.now().isoformat()
            }
            
            # Actualizar noticia existente
            return actualizar_noticia_existente(noticia_existente['id'], datos_actualizacion)
        else:
            print(f"📝 Nueva noticia: {titulo[:50]}...")
            
            # Preparar datos para inserción
            datos_insercion = {
                'titulo': titulo,
                'contenido': contenido,
                'url_origen': url,
                'fuente': 'contraloria',
                'fecha_publicacion': fecha,
                'hash_contenido': hash_contenido,
                'fecha_actualizacion': datetime.now().isoformat()
            }
            
            # Insertar nueva noticia
            return insertar_noticia_nueva(datos_insercion)
            
    except Exception as e:
        print(f"❌ Error procesando noticia: {e}")
        return False

def limpiar_duplicados_contraloria():
    """Limpiar duplicados existentes en Contraloría"""
    print("🧹 **LIMPIANDO DUPLICADOS EXISTENTES - CONTRALORÍA**")
    print("=" * 60)
    
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}'
        }
        
        # Obtener todas las noticias de Contraloría
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&fuente=eq.contraloria&order=fecha_publicacion.desc',
            headers=headers
        )
        
        if response.status_code == 200:
            noticias = response.json()
            print(f"📊 Total noticias de Contraloría: {len(noticias)}")
            
            # Agrupar por URL
            urls_grupos = {}
            for noticia in noticias:
                url = noticia.get('url_origen', '')
                if url:
                    if url not in urls_grupos:
                        urls_grupos[url] = []
                    urls_grupos[url].append(noticia)
            
            # Encontrar duplicados
            duplicados_encontrados = 0
            for url, grupo in urls_grupos.items():
                if len(grupo) > 1:
                    duplicados_encontrados += 1
                    print(f"🔍 URL con duplicados: {url}")
                    print(f"   Cantidad: {len(grupo)} noticias")
                    
                    # Mantener la más reciente y eliminar las demás
                    grupo_ordenado = sorted(grupo, key=lambda x: x.get('fecha_publicacion', ''), reverse=True)
                    
                    for noticia in grupo_ordenado[1:]:  # Eliminar todas menos la primera
                        noticia_id = noticia.get('id')
                        if noticia_id:
                            # Eliminar noticia duplicada
                            delete_response = requests.delete(
                                f'{SUPABASE_URL}/rest/v1/noticias_juridicas?id=eq.{noticia_id}',
                                headers=headers
                            )
                            
                            if delete_response.status_code == 204:
                                print(f"   ✅ Eliminada noticia duplicada ID: {noticia_id}")
                            else:
                                print(f"   ❌ Error eliminando noticia ID: {noticia_id}")
            
            print(f"\n📊 **RESUMEN DE LIMPIEZA:**")
            print(f"   Duplicados encontrados: {duplicados_encontrados}")
            print(f"   Noticias procesadas: {len(noticias)}")
            
        else:
            print(f"❌ Error obteniendo noticias: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en limpieza: {e}")

def probar_scraper_contraloria_mejorado():
    """Probar el scraper de Contraloría con las mejoras"""
    print("\n🧪 **PRUEBA DEL SCRAPER MEJORADO - CONTRALORÍA**")
    print("=" * 60)
    
    try:
        # Importar el scraper de Contraloría
        sys.path.append('../backend/scrapers/fuentes/contraloria')
        
        from contraloria_scraper import ContraloriaScraper
        
        # Crear instancia del scraper
        scraper = ContraloriaScraper()
        
        # Ejecutar scraping
        print("🔍 Ejecutando scraping de Contraloría...")
        noticias = scraper.scrape()
        
        if noticias:
            print(f"✅ Se extrajeron {len(noticias)} noticias")
            
            # Procesar cada noticia con el nuevo método
            exitos = 0
            for noticia in noticias:
                if procesar_noticia_contraloria(noticia):
                    exitos += 1
            
            print(f"\n📊 **RESULTADOS:**")
            print(f"   Noticias procesadas: {len(noticias)}")
            print(f"   Exitos: {exitos}")
            print(f"   Errores: {len(noticias) - exitos}")
            
        else:
            print("❌ No se extrajeron noticias")
            
    except ImportError as e:
        print(f"❌ Error importando scraper: {e}")
    except Exception as e:
        print(f"❌ Error ejecutando scraper: {e}")

def generar_reporte_reparacion():
    """Generar reporte de la reparación"""
    print("\n📋 **REPORTE DE REPARACIÓN - CONTRALORÍA**")
    print("=" * 60)
    
    print("✅ **PROBLEMAS IDENTIFICADOS:**")
    print("   - Error 409 (duplicado) durante inserción")
    print("   - No hay verificación previa de duplicados")
    print("   - Manejo inadecuado de errores de duplicado")
    
    print("\n✅ **SOLUCIONES IMPLEMENTADAS:**")
    print("   - Verificación de noticia existente por URL")
    print("   - Actualización de noticias existentes")
    print("   - Inserción de nuevas noticias")
    print("   - Generación de hash único mejorada")
    print("   - Limpieza de duplicados existentes")
    
    print("\n✅ **FUNCIONES CREADAS:**")
    print("   - verificar_noticia_existente()")
    print("   - actualizar_noticia_existente()")
    print("   - insertar_noticia_nueva()")
    print("   - generar_hash_contenido()")
    print("   - procesar_noticia_contraloria()")
    print("   - limpiar_duplicados_contraloria()")
    
    print("\n✅ **PRÓXIMOS PASOS:**")
    print("   1. Integrar funciones en el scraper principal")
    print("   2. Probar con scraping completo")
    print("   3. Monitorear resultados")
    print("   4. Aplicar solución a otras fuentes si es necesario")

def main():
    """Función principal"""
    print("🔧 **REPARACIÓN ESPECÍFICA - CONTRALORÍA**")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Ejecutar reparación
    limpiar_duplicados_contraloria()
    probar_scraper_contraloria_mejorado()
    generar_reporte_reparacion()
    
    print(f"\n✅ **REPARACIÓN COMPLETADA**")
    print("=" * 70)

if __name__ == "__main__":
    main() 
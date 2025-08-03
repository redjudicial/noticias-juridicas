#!/usr/bin/env python3
"""
Analizar el estado de todas las fuentes de noticias
Verificar cuáles están funcionando y cuáles no
"""

import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

# Configuración de Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://qfomiierchksyfhxoukj.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def obtener_noticias_por_fuente():
    """Obtener noticias agrupadas por fuente"""
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}'
        }
        
        # Obtener todas las noticias
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&order=fecha_publicacion.desc',
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error al obtener noticias: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return []

def analizar_fuentes():
    """Analizar el estado de todas las fuentes"""
    print("🔍 **ANÁLISIS COMPLETO DE FUENTES**")
    print("=" * 60)
    
    noticias = obtener_noticias_por_fuente()
    
    if not noticias:
        print("❌ No se pudieron obtener noticias")
        return
    
    print(f"📊 Total noticias: {len(noticias)}")
    
    # Agrupar por fuente
    fuentes = {}
    fuentes_recientes = {}  # Últimas 24 horas
    
    fecha_limite = datetime.now().replace(tzinfo=None) - timedelta(hours=24)
    
    for noticia in noticias:
        fuente = noticia['fuente']
        fecha_noticia = datetime.fromisoformat(noticia['fecha_publicacion'].replace('Z', '+00:00')).replace(tzinfo=None)
        
        if fuente not in fuentes:
            fuentes[fuente] = []
            fuentes_recientes[fuente] = []
        
        fuentes[fuente].append(noticia)
        
        if fecha_noticia > fecha_limite:
            fuentes_recientes[fuente].append(noticia)
    
    print(f"\n📰 **ESTADO DE CADA FUENTE:**")
    print("=" * 60)
    
    # Lista de fuentes esperadas
    fuentes_esperadas = [
        'poder_judicial',
        'contraloria', 
        'cde',
        'tdlc',
        '1ta',
        '3ta',
        'tribunal_ambiental',
        'sii',
        'tta',
        'inapi',
        'dt',
        'tdpi',
        'ministerio_justicia'
    ]
    
    for fuente in fuentes_esperadas:
        total = len(fuentes.get(fuente, []))
        recientes = len(fuentes_recientes.get(fuente, []))
        
        # Determinar estado
        if recientes > 0:
            estado = "🟢 ACTIVA"
            ultima_fecha = fuentes_recientes[fuente][0]['fecha_publicacion']
        elif total > 0:
            estado = "🟡 INACTIVA (tiene noticias antiguas)"
            ultima_fecha = fuentes[fuente][0]['fecha_publicacion']
        else:
            estado = "🔴 SIN NOTICIAS"
            ultima_fecha = "N/A"
        
        print(f"{estado} | {fuente:20} | Total: {total:3} | Recientes: {recientes:2} | Última: {ultima_fecha[:19] if ultima_fecha != 'N/A' else 'N/A'}")
    
    # Mostrar fuentes no esperadas
    fuentes_extra = set(fuentes.keys()) - set(fuentes_esperadas)
    if fuentes_extra:
        print(f"\n🔍 **FUENTES ADICIONALES ENCONTRADAS:**")
        print("-" * 40)
        for fuente in fuentes_extra:
            total = len(fuentes[fuente])
            recientes = len(fuentes_recientes.get(fuente, []))
            print(f"🟣 EXTRA | {fuente:20} | Total: {total:3} | Recientes: {recientes:2}")

def analizar_actividad_reciente():
    """Analizar actividad de las últimas 24 horas"""
    print(f"\n⏰ **ACTIVIDAD ÚLTIMAS 24 HORAS:**")
    print("=" * 60)
    
    noticias = obtener_noticias_por_fuente()
    
    if not noticias:
        return
    
    fecha_limite = datetime.now().replace(tzinfo=None) - timedelta(hours=24)
    noticias_recientes = []
    
    for noticia in noticias:
        fecha_noticia = datetime.fromisoformat(noticia['fecha_publicacion'].replace('Z', '+00:00')).replace(tzinfo=None)
        if fecha_noticia > fecha_limite:
            noticias_recientes.append(noticia)
    
    print(f"📊 Noticias en las últimas 24 horas: {len(noticias_recientes)}")
    
    if noticias_recientes:
        print(f"\n📰 **ÚLTIMAS NOTICIAS:**")
        print("-" * 40)
        for i, noticia in enumerate(noticias_recientes[:10], 1):
            fecha = datetime.fromisoformat(noticia['fecha_publicacion'].replace('Z', '+00:00'))
            print(f"{i:2}. [{noticia['fuente']:20}] {noticia['titulo'][:50]}... ({fecha.strftime('%H:%M')})")

def sugerir_acciones():
    """Sugerir acciones para mejorar las fuentes"""
    print(f"\n💡 **ACCIONES SUGERIDAS:**")
    print("=" * 60)
    
    print("1. 🔧 **Fuentes sin noticias recientes:**")
    print("   - Revisar si los scrapers están funcionando")
    print("   - Verificar si las URLs han cambiado")
    print("   - Comprobar si hay errores en los logs")
    
    print("\n2. 🚀 **Ejecutar scraping manual:**")
    print("   python3 backend/main.py --once --full-run --max-noticias 10")
    
    print("\n3. 📊 **Monitorear fuentes específicas:**")
    print("   - Revisar logs de cada scraper individual")
    print("   - Verificar conectividad a las fuentes")
    
    print("\n4. 🔄 **Actualizar configuración:**")
    print("   - Revisar si hay nuevas fuentes disponibles")
    print("   - Optimizar scrapers que no funcionan")

def main():
    """Función principal"""
    print("🎯 **ANÁLISIS COMPLETO DE FUENTES DE NOTICIAS**")
    print("=" * 70)
    
    # Analizar fuentes
    analizar_fuentes()
    
    # Analizar actividad reciente
    analizar_actividad_reciente()
    
    # Sugerir acciones
    sugerir_acciones()
    
    print(f"\n✅ **ANÁLISIS COMPLETADO**")
    print("=" * 70)

if __name__ == "__main__":
    main() 
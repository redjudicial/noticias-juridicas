#!/usr/bin/env python3
"""
Diagnóstico del sistema de scraping automático
Verifica por qué no se están agregando nuevas noticias
"""

import os
import sys
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

# Configuración de Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://qfomiierchksyfhxoukj.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def obtener_noticias_recientes():
    """Obtener noticias de los últimos 7 días"""
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}'
        }
        
        # Obtener noticias de los últimos 7 días
        fecha_limite = (datetime.now() - timedelta(days=7)).isoformat()
        
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&fecha_publicacion=gte.{fecha_limite}&order=fecha_publicacion.desc',
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

def analizar_actividad_reciente():
    """Analizar la actividad reciente de scraping"""
    print("🔍 **DIAGNÓSTICO DEL SCRAPING AUTOMÁTICO**")
    print("=" * 60)
    
    # Obtener noticias recientes
    noticias_recientes = obtener_noticias_recientes()
    
    if not noticias_recientes:
        print("❌ No se pudieron obtener noticias recientes")
        return
    
    print(f"📊 Total noticias en los últimos 7 días: {len(noticias_recientes)}")
    
    # Analizar por fecha
    fechas = {}
    fuentes = {}
    
    for noticia in noticias_recientes:
        fecha = noticia['fecha_publicacion'][:10]  # Solo la fecha
        fuente = noticia['fuente']
        
        fechas[fecha] = fechas.get(fecha, 0) + 1
        fuentes[fuente] = fuentes.get(fuente, 0) + 1
    
    print(f"\n📅 **ACTIVIDAD POR FECHA:**")
    print("-" * 40)
    for fecha in sorted(fechas.keys(), reverse=True):
        print(f"  {fecha}: {fechas[fecha]} noticias")
    
    print(f"\n📰 **ACTIVIDAD POR FUENTE:**")
    print("-" * 40)
    for fuente, cantidad in sorted(fuentes.items(), key=lambda x: x[1], reverse=True):
        print(f"  {fuente}: {cantidad} noticias")
    
    # Verificar la última noticia
    if noticias_recientes:
        ultima_noticia = noticias_recientes[0]
        fecha_ultima = datetime.fromisoformat(ultima_noticia['fecha_publicacion'].replace('Z', '+00:00'))
        tiempo_transcurrido = datetime.now(fecha_ultima.tzinfo) - fecha_ultima
        
        print(f"\n⏰ **ÚLTIMA NOTICIA:**")
        print("-" * 40)
        print(f"  Título: {ultima_noticia['titulo'][:50]}...")
        print(f"  Fuente: {ultima_noticia['fuente']}")
        print(f"  Fecha: {fecha_ultima.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Tiempo transcurrido: {tiempo_transcurrido}")
        
        if tiempo_transcurrido.days > 1:
            print("⚠️  ¡ALERTA! No hay noticias nuevas en más de 1 día")
        elif tiempo_transcurrido.total_seconds() > 12 * 3600:  # 12 horas en segundos
            print("⚠️  ¡ALERTA! No hay noticias nuevas en más de 12 horas")

def verificar_github_actions():
    """Verificar el estado de GitHub Actions"""
    print(f"\n🤖 **ESTADO DE GITHUB ACTIONS**")
    print("-" * 40)
    
    # Verificar horario actual
    ahora = datetime.now()
    hora_chile = ahora.hour
    dia_semana = ahora.weekday()  # 0=Lunes, 6=Domingo
    
    print(f"  Fecha actual: {ahora.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Hora en Chile: {hora_chile}:{ahora.minute:02d}")
    print(f"  Día de la semana: {['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'][dia_semana]}")
    
    # Verificar si está en horario hábil
    en_horario_habil = (dia_semana < 5 and 9 <= hora_chile <= 17)
    
    if en_horario_habil:
        print("✅ En horario hábil (GitHub Actions debería ejecutarse)")
    else:
        print("❌ Fuera de horario hábil (GitHub Actions NO se ejecuta)")
        print("   Horario configurado: Lunes-Viernes, 9:00-17:00 hora Chile")
    
    # Verificar configuración del cron
    print(f"\n📋 **CONFIGURACIÓN ACTUAL:**")
    print("-" * 40)
    print("  Cron: '0,30 12-20 * * 1-5'")
    print("  Significado: Cada 30 min, 12-20 UTC, Lunes-Viernes")
    print("  Equivale a: Cada 30 min, 9:00-17:00 hora Chile, Lunes-Viernes")

def sugerir_soluciones():
    """Sugerir soluciones al problema"""
    print(f"\n💡 **SOLUCIONES SUGERIDAS**")
    print("-" * 40)
    
    ahora = datetime.now()
    dia_semana = ahora.weekday()
    
    if dia_semana >= 5:  # Fin de semana
        print("1. 🌅 Ejecutar scraping manualmente:")
        print("   - Ir a GitHub > Actions > scraping_automatico_optimizado")
        print("   - Hacer clic en 'Run workflow'")
        print("   - Seleccionar 'test_mode: true' para prueba rápida")
    
    print("2. 🔧 Modificar horario de ejecución:")
    print("   - Cambiar cron a ejecutar también fines de semana")
    print("   - O extender horario a 24/7")
    
    print("3. 🚀 Ejecutar scraping localmente:")
    print("   python3 backend/main.py --once --working-only --max-noticias 5")
    
    print("4. 📊 Verificar logs de GitHub Actions:")
    print("   - Revisar si hay errores en las últimas ejecuciones")
    print("   - Verificar si las credenciales están correctas")

def ejecutar_scraping_manual():
    """Ejecutar scraping manual para probar"""
    print(f"\n🚀 **EJECUTANDO SCRAPING MANUAL**")
    print("-" * 40)
    
    try:
        import subprocess
        resultado = subprocess.run([
            'python3', 'backend/main.py', '--once', '--working-only', '--max-noticias', '3'
        ], capture_output=True, text=True, timeout=300)
        
        print("✅ Scraping manual completado")
        print(f"Salida: {resultado.stdout}")
        
        if resultado.stderr:
            print(f"Errores: {resultado.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout: El scraping tardó más de 5 minutos")
    except Exception as e:
        print(f"❌ Error ejecutando scraping: {e}")

def main():
    """Función principal"""
    print("🔍 **DIAGNÓSTICO COMPLETO DEL SISTEMA DE SCRAPING**")
    print("=" * 70)
    
    # Analizar actividad reciente
    analizar_actividad_reciente()
    
    # Verificar GitHub Actions
    verificar_github_actions()
    
    # Sugerir soluciones
    sugerir_soluciones()
    
    # Preguntar si ejecutar scraping manual
    print(f"\n❓ ¿Deseas ejecutar un scraping manual para probar? (s/n): ", end="")
    respuesta = input().lower().strip()
    
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        ejecutar_scraping_manual()
    
    print(f"\n✅ **DIAGNÓSTICO COMPLETADO**")
    print("=" * 70)

if __name__ == "__main__":
    main() 
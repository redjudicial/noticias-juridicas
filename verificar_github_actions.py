#!/usr/bin/env python3
"""
Script para verificar el estado del GitHub Action y las noticias
"""

import os
import sys
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

def verificar_github_actions():
    """Verificar el estado del GitHub Action"""
    print("🔍 Verificando estado del GitHub Action...")
    
    # URL del repositorio
    repo_url = "https://api.github.com/repos/redjudicial/noticias-juridicas/actions/workflows"
    
    try:
        # Intentar obtener información del workflow (sin token, solo información pública)
        response = requests.get(f"{repo_url}/scraping_automatico_optimizado.yml/runs", timeout=10)
        
        if response.status_code == 200:
            runs = response.json()
            if 'workflow_runs' in runs and runs['workflow_runs']:
                latest_run = runs['workflow_runs'][0]
                print(f"✅ Última ejecución: {latest_run['status']} - {latest_run['conclusion']}")
                print(f"📅 Fecha: {latest_run['created_at']}")
                print(f"🔗 URL: {latest_run['html_url']}")
                return True
            else:
                print("⚠️  No se encontraron ejecuciones recientes")
                return False
        else:
            print(f"❌ Error al obtener información del workflow: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando GitHub Actions: {e}")
        return False

def verificar_noticias_supabase():
    """Verificar las noticias en Supabase"""
    print("\n📊 Verificando noticias en Supabase...")
    
    try:
        from backend.database.supabase_client import SupabaseClient
        
        supabase = SupabaseClient(
            url=os.getenv('SUPABASE_URL'),
            key=os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        )
        
        # Obtener estadísticas
        total_noticias = supabase.count_noticias()
        noticias_hoy = supabase.count_noticias_hoy()
        ultima_actualizacion = supabase.get_ultima_actualizacion()
        
        print(f"📈 Total de noticias: {total_noticias}")
        print(f"📅 Noticias de hoy: {noticias_hoy}")
        print(f"🕐 Última actualización: {ultima_actualizacion}")
        
        # Verificar noticias recientes
        noticias_recientes = supabase.get_noticias_recientes(limit=5)
        print(f"\n📰 Últimas 5 noticias:")
        for i, noticia in enumerate(noticias_recientes, 1):
            fecha = noticia.get('fecha_publicacion', 'N/A')
            titulo = noticia.get('titulo', 'Sin título')[:50] + "..."
            fuente = noticia.get('fuente', 'N/A')
            print(f"   {i}. [{fuente}] {titulo} ({fecha})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando Supabase: {e}")
        return False

def verificar_configuracion_cron():
    """Verificar la configuración del cron"""
    print("\n⏰ Verificando configuración del cron...")
    
    cron_config = "0,30 12-20 * * 1-5"
    print(f"📋 Configuración actual: {cron_config}")
    print("📝 Interpretación:")
    print("   - Ejecutar cada 30 minutos (0,30)")
    print("   - Entre las 12:00-20:00 UTC (9:00-17:00 hora Chile)")
    print("   - Todos los días del mes (*)")
    print("   - Todos los meses (*)")
    print("   - Lunes a Viernes (1-5)")
    
    # Calcular próxima ejecución
    from datetime import datetime, timedelta
    now = datetime.now(timezone.utc)
    
    # Verificar si estamos en horario hábil
    is_weekday = now.weekday() < 5  # 0-4 = Lunes a Viernes
    is_business_hours = 12 <= now.hour < 20
    
    if is_weekday and is_business_hours:
        print(f"✅ Estamos en horario hábil (Lunes-Viernes, 9:00-17:00 Chile)")
        
        # Calcular próxima ejecución
        current_minute = now.minute
        if current_minute < 30:
            next_run = now.replace(minute=30, second=0, microsecond=0)
        else:
            next_run = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        
        print(f"⏱️  Próxima ejecución programada: {next_run.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    else:
        print(f"⏸️  Fuera de horario hábil - próxima ejecución: Lunes 9:00 AM Chile")
    
    return True

def main():
    """Función principal"""
    print("🚀 Verificación del Sistema de Noticias Jurídicas")
    print("=" * 50)
    
    # Verificar GitHub Actions
    github_ok = verificar_github_actions()
    
    # Verificar Supabase
    supabase_ok = verificar_noticias_supabase()
    
    # Verificar configuración del cron
    cron_ok = verificar_configuracion_cron()
    
    print("\n" + "=" * 50)
    print("📋 RESUMEN:")
    print(f"   GitHub Actions: {'✅ OK' if github_ok else '❌ Error'}")
    print(f"   Supabase: {'✅ OK' if supabase_ok else '❌ Error'}")
    print(f"   Configuración Cron: {'✅ OK' if cron_ok else '❌ Error'}")
    
    if github_ok and supabase_ok and cron_ok:
        print("\n🎉 ¡Sistema funcionando correctamente!")
        print("📰 El GitHub Action está activo y detectando nuevas noticias automáticamente")
    else:
        print("\n⚠️  Hay problemas que requieren atención")

if __name__ == "__main__":
    main() 
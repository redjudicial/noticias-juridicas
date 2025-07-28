#!/usr/bin/env python3
"""
Script para configurar GitHub Actions y automatización del scraping
"""

import os
import sys
from datetime import datetime

def mostrar_configuracion_github_actions():
    """Mostrar configuración de GitHub Actions"""
    print("🚀 CONFIGURACIÓN DE GITHUB ACTIONS")
    print("=" * 60)
    
    print("📋 WORKFLOW CONFIGURADO:")
    print("   Archivo: .github/workflows/scraping_automatico.yml")
    print("   Frecuencia: Cada 15 minutos")
    print("   Horario: Lunes a Sábado, 8:00-18:00 hora Chile")
    print("   Ejecución manual: Disponible")
    print("   Modo prueba: Disponible")
    print()
    
    print("⏰ CRON SCHEDULE:")
    print("   '0,15,30,45 11-21 * * 1-6'")
    print("   • 0,15,30,45 = cada 15 minutos")
    print("   • 11-21 = 8:00-18:00 hora Chile (UTC-3)")
    print("   • 1-6 = Lunes a Sábado")
    print()
    
    print("🔧 JOBS CONFIGURADOS:")
    print("   1. scraping-noticias: Ejecuta el scraping")
    print("   2. monitoreo: Genera estadísticas y verifica BD")
    print()

def mostrar_secrets_necesarios():
    """Mostrar secrets necesarios para GitHub Actions"""
    print("🔐 SECRETS NECESARIOS EN GITHUB")
    print("=" * 50)
    
    secrets = [
        {
            'name': 'SUPABASE_URL',
            'description': 'URL de tu proyecto Supabase',
            'example': 'https://qfomiierchksyfhxoukj.supabase.co',
            'required': True
        },
        {
            'name': 'SUPABASE_ANON_KEY',
            'description': 'Clave anónima de Supabase',
            'example': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
            'required': True
        },
        {
            'name': 'SUPABASE_SERVICE_ROLE_KEY',
            'description': 'Clave de servicio de Supabase',
            'example': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
            'required': True
        },
        {
            'name': 'OPENAI_API_KEY',
            'description': 'Clave de API de OpenAI',
            'example': 'sk-proj-...',
            'required': True
        }
    ]
    
    for secret in secrets:
        status = "✅ REQUERIDO" if secret['required'] else "⚪ OPCIONAL"
        print(f"{status} {secret['name']}")
        print(f"   Descripción: {secret['description']}")
        print(f"   Ejemplo: {secret['example']}")
        print()

def mostrar_instrucciones_configuracion():
    """Mostrar instrucciones para configurar secrets"""
    print("📝 INSTRUCCIONES PARA CONFIGURAR SECRETS")
    print("=" * 50)
    
    instrucciones = [
        "1. Ve a tu repositorio en GitHub",
        "2. Haz clic en 'Settings' (Configuración)",
        "3. En el menú lateral, haz clic en 'Secrets and variables' → 'Actions'",
        "4. Haz clic en 'New repository secret'",
        "5. Agrega cada secret con su nombre y valor correspondiente:",
        "",
        "   SUPABASE_URL = https://tu-proyecto.supabase.co",
        "   SUPABASE_ANON_KEY = tu-clave-anonima",
        "   SUPABASE_SERVICE_ROLE_KEY = tu-clave-servicio",
        "   OPENAI_API_KEY = tu-clave-openai",
        "",
        "6. Haz clic en 'Add secret' para cada uno",
        "7. Verifica que todos los secrets estén configurados",
        "8. El workflow se ejecutará automáticamente según el cron"
    ]
    
    for instruccion in instrucciones:
        print(f"   {instruccion}")

def mostrar_beneficios_github_actions():
    """Mostrar beneficios de usar GitHub Actions"""
    print("🎯 BENEFICIOS DE GITHUB ACTIONS")
    print("=" * 40)
    
    beneficios = [
        "✅ **Gratis**: 2,000 minutos/mes en cuentas gratuitas",
        "✅ **Automático**: Sin necesidad de servidor propio",
        "✅ **Confiable**: Infraestructura de GitHub",
        "✅ **Escalable**: Se ajusta automáticamente",
        "✅ **Monitoreo**: Logs y estadísticas integradas",
        "✅ **Notificaciones**: Alertas automáticas",
        "✅ **Backup**: Código y configuración en GitHub",
        "✅ **Colaboración**: Múltiples desarrolladores",
        "✅ **Versionado**: Control de cambios automático",
        "✅ **Seguridad**: Secrets encriptados"
    ]
    
    for beneficio in beneficios:
        print(beneficio)

def calcular_uso_minutos():
    """Calcular uso estimado de minutos"""
    print("📊 CÁLCULO DE USO DE MINUTOS")
    print("=" * 40)
    
    # Cálculos
    ejecuciones_por_hora = 4  # Cada 15 minutos
    horas_por_dia = 10  # 8:00-18:00
    dias_por_semana = 6  # Lunes a Sábado
    semanas_por_mes = 4.33  # Promedio
    
    ejecuciones_por_dia = ejecuciones_por_hora * horas_por_dia
    ejecuciones_por_semana = ejecuciones_por_dia * dias_por_semana
    ejecuciones_por_mes = ejecuciones_por_semana * semanas_por_mes
    
    minutos_por_ejecucion = 5  # Estimado
    minutos_por_mes = ejecuciones_por_mes * minutos_por_ejecucion
    
    print(f"⏱️  Ejecuciones por hora: {ejecuciones_por_hora}")
    print(f"⏱️  Horas por día: {horas_por_dia}")
    print(f"⏱️  Días por semana: {dias_por_semana}")
    print(f"⏱️  Ejecuciones por día: {ejecuciones_por_dia}")
    print(f"⏱️  Ejecuciones por semana: {ejecuciones_por_semana}")
    print(f"⏱️  Ejecuciones por mes: {ejecuciones_por_mes:.0f}")
    print(f"⏱️  Minutos por ejecución: {minutos_por_ejecucion}")
    print(f"⏱️  Minutos por mes: {minutos_por_mes:.0f}")
    print()
    
    if minutos_por_mes <= 2000:
        print("✅ USO DENTRO DEL LÍMITE GRATUITO")
        print(f"   Límite: 2,000 minutos/mes")
        print(f"   Uso estimado: {minutos_por_mes:.0f} minutos/mes")
        print(f"   Margen: {2000 - minutos_por_mes:.0f} minutos disponibles")
    else:
        print("⚠️  USO EXCEDE EL LÍMITE GRATUITO")
        print(f"   Límite: 2,000 minutos/mes")
        print(f"   Uso estimado: {minutos_por_mes:.0f} minutos/mes")
        print(f"   Exceso: {minutos_por_mes - 2000:.0f} minutos")

def mostrar_estado_actual():
    """Mostrar estado actual del proyecto"""
    print("📈 ESTADO ACTUAL DEL PROYECTO")
    print("=" * 40)
    
    estado = {
        'scrapers_funcionando': 2,
        'scrapers_pendientes': 6,
        'total_fuentes': 8,
        'esquema_estandarizado': True,
        'frontend_unificado': True,
        'supabase_configurado': True,
        'github_actions_ready': True
    }
    
    print(f"🔧 Scrapers funcionando: {estado['scrapers_funcionando']}/{estado['total_fuentes']}")
    print(f"🔧 Scrapers pendientes: {estado['scrapers_pendientes']}/{estado['total_fuentes']}")
    print(f"✅ Esquema estandarizado: {'Sí' if estado['esquema_estandarizado'] else 'No'}")
    print(f"✅ Frontend unificado: {'Sí' if estado['frontend_unificado'] else 'No'}")
    print(f"✅ Supabase configurado: {'Sí' if estado['supabase_configurado'] else 'No'}")
    print(f"✅ GitHub Actions listo: {'Sí' if estado['github_actions_ready'] else 'No'}")
    print()
    
    progreso = (estado['scrapers_funcionando'] / estado['total_fuentes']) * 100
    print(f"📊 Progreso general: {progreso:.1f}%")

def main():
    """Función principal"""
    print("🚀 CONFIGURACIÓN DE AUTOMATIZACIÓN CON GITHUB ACTIONS")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Mostrar estado actual
    mostrar_estado_actual()
    print()
    
    # Mostrar configuración de GitHub Actions
    mostrar_configuracion_github_actions()
    
    # Mostrar secrets necesarios
    mostrar_secrets_necesarios()
    
    # Mostrar instrucciones
    mostrar_instrucciones_configuracion()
    print()
    
    # Mostrar beneficios
    mostrar_beneficios_github_actions()
    print()
    
    # Calcular uso de minutos
    calcular_uso_minutos()
    print()
    
    print("🎯 PRÓXIMOS PASOS:")
    print("1. Configurar secrets en GitHub")
    print("2. Hacer commit y push del workflow")
    print("3. Verificar que el workflow se ejecute correctamente")
    print("4. Monitorear logs y estadísticas")
    print("5. Implementar scrapers pendientes")
    print("6. Activar scraping automático completo")
    
    print()
    print("✅ CONFIGURACIÓN LISTA PARA AUTOMATIZACIÓN")

if __name__ == "__main__":
    main() 
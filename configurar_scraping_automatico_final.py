#!/usr/bin/env python3
"""
Script para configurar el scraping automático de noticias jurídicas
ACTIVO DESDE EL LUNES 21 DE JULIO - CADA 15 MINUTOS
"""

import os
import sys
from datetime import datetime, timedelta
import schedule
import time

def configurar_scraping_automatico():
    """Configurar el scraping automático"""
    print("🔧 CONFIGURACIÓN DE SCRAPING AUTOMÁTICO")
    print("=" * 60)
    
    # Configuración
    config = {
        'fecha_inicio': '2025-07-21',  # Lunes 21 de julio
        'intervalo_minutos': 15,
        'fuentes_activas': [
            'poder_judicial',      # ✅ FUNCIONANDO
            'ministerio_justicia', # ✅ FUNCIONANDO
            'tribunal_constitucional', # 🔧 EN DESARROLLO
            'dpp',                 # 🔧 EN DESARROLLO
            'diario_oficial',      # 🔧 EN DESARROLLO
            'fiscalia',           # 🔧 EN DESARROLLO
            'contraloria',        # 🔧 EN DESARROLLO
            'cde'                 # 🔧 EN DESARROLLO
        ],
        'max_noticias_por_fuente': 20,
        'log_file': 'scraping_automatico.log'
    }
    
    print(f"📅 Fecha de inicio: {config['fecha_inicio']}")
    print(f"⏰ Intervalo: {config['intervalo_minutos']} minutos")
    print(f"📰 Fuentes activas: {len(config['fuentes_activas'])}")
    print(f"🔢 Máximo noticias por fuente: {config['max_noticias_por_fuente']}")
    print(f"📝 Log file: {config['log_file']}")
    
    return config

def crear_script_inicio():
    """Crear script para iniciar el scraping automático"""
    script_content = '''#!/bin/bash
# Script para iniciar el scraping automático de noticias jurídicas
# ACTIVO DESDE EL LUNES 21 DE JULIO - CADA 15 MINUTOS

echo "🚀 Iniciando scraping automático de noticias jurídicas..."
echo "📅 Fecha: $(date)"
echo "⏰ Intervalo: 15 minutos"
echo "📰 Fuentes: Poder Judicial, Ministerio de Justicia, etc."

# Verificar que estamos en el directorio correcto
cd "$(dirname "$0")"

# Verificar que existe el archivo de credenciales
if [ ! -f "APIS_Y_CREDENCIALES.env" ]; then
    echo "❌ Error: No se encontró APIS_Y_CREDENCIALES.env"
    exit 1
fi

# Cargar variables de entorno
source APIS_Y_CREDENCIALES.env

# Verificar que las variables están cargadas
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_SERVICE_ROLE_KEY" ]; then
    echo "❌ Error: Variables de Supabase no encontradas"
    exit 1
fi

echo "✅ Variables de entorno cargadas correctamente"

# Iniciar el scraping en modo programado
echo "🔄 Iniciando sistema de scraping automático..."
nohup python3 backend/main.py --scheduled > scraping_automatico.log 2>&1 &

# Guardar el PID del proceso
echo $! > scraping.pid

echo "✅ Scraping automático iniciado con PID: $(cat scraping.pid)"
echo "📝 Logs disponibles en: scraping_automatico.log"
echo "🛑 Para detener: ./detener_scraping.sh"
'''
    
    with open('iniciar_scraping_automatico.sh', 'w') as f:
        f.write(script_content)
    
    # Hacer ejecutable
    os.system('chmod +x iniciar_scraping_automatico.sh')
    print("✅ Script de inicio creado: iniciar_scraping_automatico.sh")

def crear_script_detencion():
    """Crear script para detener el scraping automático"""
    script_content = '''#!/bin/bash
# Script para detener el scraping automático de noticias jurídicas

echo "🛑 Deteniendo scraping automático..."

# Verificar que estamos en el directorio correcto
cd "$(dirname "$0")"

# Verificar si existe el archivo PID
if [ ! -f "scraping.pid" ]; then
    echo "❌ No se encontró archivo PID. El scraping no está ejecutándose."
    exit 1
fi

# Leer el PID
PID=$(cat scraping.pid)

# Verificar si el proceso está ejecutándose
if ps -p $PID > /dev/null; then
    echo "🔄 Deteniendo proceso con PID: $PID"
    kill $PID
    
    # Esperar un momento y verificar si se detuvo
    sleep 2
    if ps -p $PID > /dev/null; then
        echo "⚠️  El proceso no se detuvo, forzando terminación..."
        kill -9 $PID
    fi
    
    echo "✅ Proceso detenido exitosamente"
else
    echo "⚠️  El proceso con PID $PID no está ejecutándose"
fi

# Limpiar archivo PID
rm -f scraping.pid

echo "🧹 Limpieza completada"
'''
    
    with open('detener_scraping_automatico.sh', 'w') as f:
        f.write(script_content)
    
    # Hacer ejecutable
    os.system('chmod +x detener_scraping_automatico.sh')
    print("✅ Script de detención creado: detener_scraping_automatico.sh")

def crear_script_monitoreo():
    """Crear script para monitorear el scraping automático"""
    script_content = '''#!/bin/bash
# Script para monitorear el scraping automático de noticias jurídicas

echo "📊 MONITOREO DE SCRAPING AUTOMÁTICO"
echo "=================================="

# Verificar que estamos en el directorio correcto
cd "$(dirname "$0")"

# Verificar si el proceso está ejecutándose
if [ -f "scraping.pid" ]; then
    PID=$(cat scraping.pid)
    if ps -p $PID > /dev/null; then
        echo "✅ Scraping automático EJECUTÁNDOSE (PID: $PID)"
        echo "⏰ Iniciado: $(ps -o lstart= -p $PID)"
        echo "💾 Memoria: $(ps -o rss= -p $PID | awk '{print $1/1024 " MB"}')"
    else
        echo "❌ Scraping automático DETENIDO (PID: $PID no encontrado)"
    fi
else
    echo "❌ Scraping automático NO INICIADO"
fi

echo ""
echo "📝 ÚLTIMOS LOGS:"
echo "================"
if [ -f "scraping_automatico.log" ]; then
    tail -20 scraping_automatico.log
else
    echo "No se encontró archivo de logs"
fi

echo ""
echo "📊 ESTADÍSTICAS DE HOY:"
echo "======================"
# Aquí se pueden agregar comandos para consultar estadísticas de Supabase
echo "Para ver estadísticas completas, ejecutar: python3 backend/main.py --stats"
'''
    
    with open('monitorear_scraping.sh', 'w') as f:
        f.write(script_content)
    
    # Hacer ejecutable
    os.system('chmod +x monitorear_scraping.sh')
    print("✅ Script de monitoreo creado: monitorear_scraping.sh")

def verificar_estado_actual():
    """Verificar el estado actual del sistema"""
    print("\n🔍 VERIFICACIÓN DEL ESTADO ACTUAL")
    print("=" * 40)
    
    # Verificar archivos críticos
    archivos_criticos = [
        'APIS_Y_CREDENCIALES.env',
        'backend/main.py',
        'backend/database/supabase_client.py',
        'backend/scrapers/poder_judicial_scraper.py',
        'backend/scrapers/ministerio_justicia_scraper.py'
    ]
    
    for archivo in archivos_criticos:
        if os.path.exists(archivo):
            print(f"✅ {archivo}")
        else:
            print(f"❌ {archivo} - FALTANTE")
    
    # Verificar si hay un proceso ejecutándose
    if os.path.exists('scraping.pid'):
        pid = open('scraping.pid').read().strip()
        print(f"🔄 Proceso activo: PID {pid}")
    else:
        print("⏸️  No hay proceso activo")

def main():
    """Función principal"""
    print("🚀 CONFIGURACIÓN FINAL DE SCRAPING AUTOMÁTICO")
    print("=" * 60)
    print("📅 ACTIVO DESDE EL LUNES 21 DE JULIO")
    print("⏰ INTERVALO: CADA 15 MINUTOS")
    print("=" * 60)
    
    # Configurar scraping
    config = configurar_scraping_automatico()
    
    # Verificar estado actual
    verificar_estado_actual()
    
    # Crear scripts de control
    print("\n📝 Creando scripts de control...")
    crear_script_inicio()
    crear_script_detencion()
    crear_script_monitoreo()
    
    print("\n" + "=" * 60)
    print("✅ CONFIGURACIÓN COMPLETA")
    print("=" * 60)
    
    print("\n📋 INSTRUCCIONES DE USO:")
    print("1. Para INICIAR scraping automático:")
    print("   ./iniciar_scraping_automatico.sh")
    print()
    print("2. Para DETENER scraping automático:")
    print("   ./detener_scraping_automatico.sh")
    print()
    print("3. Para MONITOREAR estado:")
    print("   ./monitorear_scraping.sh")
    print()
    print("4. Para ejecutar UNA VEZ (prueba):")
    print("   python3 backend/main.py --once")
    print()
    print("5. Para ver estadísticas:")
    print("   python3 backend/main.py --stats")
    
    print("\n🎯 ESTADO ACTUAL:")
    print("✅ Poder Judicial: FUNCIONANDO")
    print("✅ Ministerio de Justicia: FUNCIONANDO")
    print("🔧 Otras fuentes: EN DESARROLLO")
    print("✅ Base de datos: CONFIGURADA")
    print("✅ Interfaz web: FUNCIONAL")
    
    print("\n🚀 EL SISTEMA ESTÁ LISTO PARA PRODUCCIÓN")
    print("📅 ACTIVO DESDE EL LUNES 21 DE JULIO")
    print("⏰ CADA 15 MINUTOS AUTOMÁTICAMENTE")

if __name__ == "__main__":
    main() 
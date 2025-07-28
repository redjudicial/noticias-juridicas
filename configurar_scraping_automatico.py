#!/usr/bin/env python3
"""
Script para configurar el scraping automático de noticias jurídicas
Comenzará el lunes 21 de julio, cada 15 minutos
"""

import os
import sys
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

def configurar_scraping_automatico():
    """Configurar el sistema de scraping automático"""
    
    print("🔧 Configurando scraping automático de noticias jurídicas")
    print("=" * 60)
    
    # Fecha de inicio: Lunes 21 de julio
    fecha_inicio = datetime(2025, 7, 21, 9, 0, 0, tzinfo=timezone.utc)  # 9:00 AM UTC
    ahora = datetime.now(timezone.utc)
    
    print(f"📅 Fecha actual: {ahora.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🚀 Fecha de inicio: {fecha_inicio.strftime('%d/%m/%Y %H:%M:%S')}")
    
    if ahora < fecha_inicio:
        dias_restantes = (fecha_inicio - ahora).days
        horas_restantes = ((fecha_inicio - ahora).seconds // 3600)
        print(f"⏰ Tiempo restante: {dias_restantes} días, {horas_restantes} horas")
    else:
        print("✅ ¡Ya es momento de comenzar el scraping automático!")
    
    print("\n📋 Configuración del sistema:")
    print("   • Intervalo: 15 minutos")
    print("   • Fuentes: 8 fuentes oficiales")
    print("   • Base de datos: Supabase")
    print("   • Logs: Completos con métricas")
    
    print("\n🔧 Comandos para activar:")
    print("   # Para ejecutar manualmente:")
    print("   python3 backend/main.py --once")
    print("")
    print("   # Para activar scraping automático:")
    print("   python3 backend/main.py --scheduled")
    print("")
    print("   # Para ejecutar en background (recomendado):")
    print("   nohup python3 backend/main.py --scheduled > scraping.log 2>&1 &")
    
    print("\n📊 Monitoreo:")
    print("   # Ver logs en tiempo real:")
    print("   tail -f scraping.log")
    print("")
    print("   # Ver estadísticas:")
    print("   python3 test_sistema.py")
    
    print("\n🎯 Próximos pasos:")
    print("   1. ✅ Sistema configurado y probado")
    print("   2. ✅ Base de datos lista")
    print("   3. ✅ Interfaz web funcional")
    print("   4. 🔄 Lunes 21/07: Activar scraping automático")
    print("   5. 📈 Monitorear resultados")
    
    return True

def crear_script_inicio():
    """Crear script para iniciar el scraping automático"""
    
    script_content = """#!/bin/bash
# Script para iniciar el scraping automático de noticias jurídicas
# Ejecutar: ./iniciar_scraping.sh

echo "🚀 Iniciando scraping automático de noticias jurídicas..."
echo "📅 Fecha: $(date)"
echo "⏰ Intervalo: 15 minutos"

# Navegar al directorio del proyecto
cd "$(dirname "$0")"

# Verificar que existe el archivo principal
if [ ! -f "backend/main.py" ]; then
    echo "❌ Error: No se encuentra backend/main.py"
    exit 1
fi

# Verificar variables de entorno
if [ ! -f "APIS_Y_CREDENCIALES.env" ]; then
    echo "❌ Error: No se encuentra APIS_Y_CREDENCIALES.env"
    exit 1
fi

# Iniciar scraping en background
echo "🔄 Iniciando proceso en background..."
nohup python3 backend/main.py --scheduled > scraping.log 2>&1 &

# Guardar PID del proceso
echo $! > scraping.pid

echo "✅ Scraping iniciado con PID: $(cat scraping.pid)"
echo "📋 Para ver logs: tail -f scraping.log"
echo "🛑 Para detener: ./detener_scraping.sh"
"""
    
    with open('iniciar_scraping.sh', 'w') as f:
        f.write(script_content)
    
    # Hacer ejecutable
    os.system('chmod +x iniciar_scraping.sh')
    
    print("✅ Script de inicio creado: iniciar_scraping.sh")

def crear_script_detencion():
    """Crear script para detener el scraping automático"""
    
    script_content = """#!/bin/bash
# Script para detener el scraping automático de noticias jurídicas
# Ejecutar: ./detener_scraping.sh

echo "🛑 Deteniendo scraping automático..."

# Verificar si existe el archivo PID
if [ ! -f "scraping.pid" ]; then
    echo "❌ No se encuentra archivo PID. El proceso puede no estar ejecutándose."
    exit 1
fi

# Leer PID
PID=$(cat scraping.pid)

# Verificar si el proceso está ejecutándose
if ps -p $PID > /dev/null; then
    echo "🔄 Deteniendo proceso con PID: $PID"
    kill $PID
    
    # Esperar un momento y verificar
    sleep 2
    if ps -p $PID > /dev/null; then
        echo "⚠️  Proceso no se detuvo, forzando terminación..."
        kill -9 $PID
    fi
    
    echo "✅ Proceso detenido exitosamente"
else
    echo "⚠️  Proceso con PID $PID no está ejecutándose"
fi

# Limpiar archivo PID
rm -f scraping.pid

echo "📋 Logs disponibles en: scraping.log"
"""
    
    with open('detener_scraping.sh', 'w') as f:
        f.write(script_content)
    
    # Hacer ejecutable
    os.system('chmod +x detener_scraping.sh')
    
    print("✅ Script de detención creado: detener_scraping.sh")

def main():
    """Función principal"""
    
    print("🔧 CONFIGURACIÓN DE SCRAPING AUTOMÁTICO")
    print("=" * 60)
    
    # Configurar sistema
    configurar_scraping_automatico()
    
    # Crear scripts de control
    print("\n📝 Creando scripts de control...")
    crear_script_inicio()
    crear_script_detencion()
    
    print("\n" + "=" * 60)
    print("✅ CONFIGURACIÓN COMPLETA")
    print("=" * 60)
    print("📋 Resumen:")
    print("   • Sistema listo para scraping automático")
    print("   • Inicio: Lunes 21 de julio, 9:00 AM")
    print("   • Intervalo: 15 minutos")
    print("   • Scripts de control creados")
    print("")
    print("🚀 Para activar el lunes 21:")
    print("   ./iniciar_scraping.sh")
    print("")
    print("📊 Para monitorear:")
    print("   tail -f scraping.log")
    print("")
    print("🛑 Para detener:")
    print("   ./detener_scraping.sh")

if __name__ == "__main__":
    main() 
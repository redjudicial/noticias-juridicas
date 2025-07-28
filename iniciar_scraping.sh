#!/bin/bash
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

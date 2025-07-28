#!/bin/bash
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

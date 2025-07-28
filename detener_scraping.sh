#!/bin/bash
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

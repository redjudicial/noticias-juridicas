#!/bin/bash
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

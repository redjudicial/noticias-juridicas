#!/bin/bash
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

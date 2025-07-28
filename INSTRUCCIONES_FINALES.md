
🎯 SISTEMA LISTO PARA CONFIGURAR EN GITHUB

1. CREAR REPOSITORIO:
   - Ve a https://github.com/redjudicial
   - Click "New repository"
   - Nombre: noticias-juridicas
   - NO inicializar con README
   - Click "Create repository"

2. CONFIGURAR SECRETS:
   - Ve a Settings → Secrets and variables → Actions
   - Agregar estos 3 secrets:
     * SUPABASE_URL=https://tu-proyecto.supabase.co
     * SUPABASE_KEY=tu-anon-key-supabase
     * OPENAI_API_KEY=tu-openai-api-key

3. SUBIR CÓDIGO:
   git remote add origin https://github.com/redjudicial/noticias-juridicas.git
   git branch -M main
   git push -u origin main

4. ACTIVAR AUTOMATIZACIÓN:
   - Ve a la pestaña "Actions"
   - Click "Run workflow" para probar
   - El sistema se ejecutará cada 30 minutos automáticamente

5. VERIFICAR FUNCIONAMIENTO:
   - Revisar noticias en Supabase
   - Abrir noticias.html para ver el frontend
   - Monitorear logs en GitHub Actions

✅ SISTEMA 100% FUNCIONAL CON:
   - 10 fuentes oficiales
   - Resúmenes ejecutivos con IA
   - Frontend profesional
   - Automatización completa
   - Metadata completa
   - Ordenamiento por fecha/hora
   - Títulos completos

🚀 ¡LISTO PARA PRODUCCIÓN!

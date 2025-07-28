# 🚀 CONFIGURACIÓN DE GITHUB ACTIONS PARA AUTOMATIZACIÓN

## 📋 PASOS PARA CONFIGURAR LA AUTOMATIZACIÓN

### 1. **Crear Repositorio en GitHub**
```bash
# En la cuenta redjudicial (NO docemonos)
# Crear nuevo repositorio: noticias-juridicas
```

### 2. **Configurar Secrets en GitHub**
Ir a: `Settings > Secrets and variables > Actions`

Agregar los siguientes secrets:
- `SUPABASE_URL`: URL de tu proyecto Supabase
- `SUPABASE_KEY`: API Key de Supabase
- `OPENAI_API_KEY`: API Key de OpenAI

### 3. **Subir Código al Repositorio**
```bash
# Inicializar git (si no está inicializado)
git init

# Agregar remoto
git remote add origin https://github.com/redjudicial/noticias-juridicas.git

# Agregar archivos
git add .

# Commit inicial
git commit -m "🚀 Sistema de noticias jurídicas - Implementación inicial"

# Push al repositorio
git push -u origin main
```

### 4. **Verificar Workflow**
- Ir a la pestaña "Actions" en GitHub
- Verificar que el workflow aparezca
- Hacer commit manual para probar

### 5. **Configuración del Cron**
El workflow está configurado para ejecutarse:
- **Frecuencia**: Cada 30 minutos
- **Horario**: 9:00-17:00 (horario chileno)
- **Días**: Lunes a Viernes
- **Zona horaria**: UTC-3

### 6. **Monitoreo**
- **Logs**: Revisar la pestaña Actions en GitHub
- **Notificaciones**: Configurar webhooks si es necesario
- **Métricas**: Revisar logs_scraping.txt

## 🔧 CONFIGURACIÓN ADICIONAL

### Variables de Entorno
```bash
# En el workflow se configuran automáticamente:
SUPABASE_URL=${{ secrets.SUPABASE_URL }}
SUPABASE_KEY=${{ secrets.SUPABASE_KEY }}
OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}
```

### Límites de GitHub Actions
- **Cuenta gratuita**: 2,000 minutos/mes
- **Nuestro uso**: ~480 minutos/mes (16 horas)
- **Disponible**: 1,520 minutos restantes

## 📊 ESTADÍSTICAS ESPERADAS

### Por Ejecución
- **Tiempo**: ~2-3 minutos
- **Noticias**: ~50-100 noticias
- **Fuentes**: 10 fuentes activas

### Por Mes
- **Ejecuciones**: ~480 ejecuciones
- **Noticias totales**: ~24,000-48,000 noticias
- **Costo**: $0 (dentro del límite gratuito)

## 🚨 SOLUCIÓN DE PROBLEMAS

### Error: "Secrets not found"
- Verificar que los secrets estén configurados correctamente
- Revisar nombres exactos de las variables

### Error: "Python dependencies"
- Verificar que requirements.txt esté actualizado
- Revisar versiones de Python

### Error: "Supabase connection"
- Verificar URL y API Key de Supabase
- Revisar permisos de la base de datos

## 📞 SOPORTE

Para problemas técnicos:
1. Revisar logs en GitHub Actions
2. Verificar configuración de secrets
3. Probar ejecución manual
4. Contactar al equipo de desarrollo

---

**✅ ESTADO**: Listo para implementación
**🎯 PRÓXIMO PASO**: Configurar repositorio en GitHub 
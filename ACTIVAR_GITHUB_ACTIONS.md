# 🚀 ACTIVAR GITHUB ACTIONS AUTOMÁTICO

**Fecha:** 3 de Agosto 2025  
**Workflow:** `scraping_automatico_optimizado.yml`  
**Estado:** ✅ CONFIGURADO, REQUIERE ACTIVACIÓN MANUAL

## 📋 PASOS PARA ACTIVAR

### **1. ACCEDER A GITHUB ACTIONS**
```
🌐 URL: https://github.com/redjudicial/noticias-juridicas/actions
```

### **2. SELECCIONAR WORKFLOW**
- Buscar: `scraping_automatico_optimizado`
- Hacer clic en el workflow

### **3. EJECUTAR MANUALMENTE**
- Hacer clic en botón: **"Run workflow"**
- Branch: `main` (por defecto)
- Parámetros: Dejar vacíos (modo automático)
- Hacer clic en: **"Run workflow"**

### **4. VERIFICAR ACTIVACIÓN**
- El workflow se ejecutará inmediatamente
- Después de la primera ejecución, el schedule se activará automáticamente
- Se ejecutará cada hora en punto (cron: `'0 * * * *'`)

## ⚙️ CONFIGURACIÓN ACTUAL

### **SCHEDULE (CRON)**
```yaml
on:
  schedule:
    - cron: '0 * * * *'  # Cada hora en minuto 0
  workflow_dispatch:     # Ejecución manual
```

### **MODOS DE EJECUCIÓN**
```bash
# Modo automático (por defecto)
python3 backend/main.py --once --working-only --max-noticias 3

# Modo prueba (manual)
python3 backend/main.py --once --test-mode --max-noticias 5

# Modo completo (manual)
python3 backend/main.py --once --max-noticias 10
```

## 🔍 VERIFICACIÓN

### **COMPROBAR QUE FUNCIONA**
1. **Ejecutar manualmente** una vez
2. **Esperar 1 hora** para verificar ejecución automática
3. **Revisar logs** en GitHub Actions
4. **Verificar Supabase** para nuevas noticias

### **MONITOREO**
```bash
# Verificar noticias en Supabase
# URL: https://qfomiierchksyfhxoukj.supabase.co
# Tabla: noticias_juridicas
```

## 🚨 SOLUCIÓN DE PROBLEMAS

### **SI NO SE EJECUTA AUTOMÁTICAMENTE**
1. **Verificar que GitHub tiene permisos** para ejecutar schedules
2. **Revisar que el repositorio es público** (GitHub Actions gratuitos)
3. **Comprobar que no hay errores** en la última ejecución manual

### **SI HAY ERRORES**
1. **Revisar logs** en GitHub Actions
2. **Verificar variables de entorno** (secrets)
3. **Comprobar dependencias** (requirements.txt)

## 📊 ESTADO DESPUÉS DE ACTIVACIÓN

### **✅ FUNCIONAMIENTO ESPERADO**
- **Cada hora**: Scraping automático de 3 noticias por fuente
- **Fuentes activas**: Solo las que funcionan correctamente
- **Base de datos**: Actualización automática en Supabase
- **Frontend**: Actualización automática en redjudicial.cl

### **📈 MÉTRICAS**
- **Frecuencia**: Cada hora (24/7)
- **Noticias por ejecución**: ~30-50 noticias
- **Fuentes activas**: 13 fuentes jurídicas
- **Tiempo de ejecución**: ~5-10 minutos

## 🎯 RESULTADO FINAL

Una vez activado, el sistema funcionará completamente automático:

```
🕐 00:00 → Scraping automático
🕐 01:00 → Scraping automático  
🕐 02:00 → Scraping automático
...
🕐 23:00 → Scraping automático
```

**¡El sistema estará 100% automatizado!** 🚀

---
**Última actualización:** 3 de Agosto 2025  
**Estado:** ✅ LISTO PARA ACTIVACIÓN 
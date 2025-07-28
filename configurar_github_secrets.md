# 🔧 Configuración de GitHub Actions Secrets

## **📋 PASOS PARA CONFIGURAR AUTOMATIZACIÓN**

### **1. Configurar Secrets en GitHub**

Ve a tu repositorio en GitHub:
1. **Settings** → **Secrets and variables** → **Actions**
2. Agregar los siguientes secrets:

```
SUPABASE_URL=tu_url_de_supabase
SUPABASE_ANON_KEY=tu_anon_key_de_supabase  
OPENAI_API_KEY=tu_api_key_de_openai
```

### **2. Verificar Workflow**

El archivo `.github/workflows/scraping_noticias.yml` ya está configurado para:
- ✅ Ejecutarse **cada 30 minutos** automáticamente
- ✅ Permitir ejecución manual desde GitHub
- ✅ Instalar dependencias automáticamente
- ✅ Configurar variables de entorno
- ✅ Ejecutar el scraping

### **3. Activar el Workflow**

Una vez configurados los secrets:
1. Ve a **Actions** en tu repositorio
2. Selecciona **"Scraping Noticias Jurídicas"**
3. Haz clic en **"Run workflow"** para probar manualmente

### **4. Monitoreo**

- 📊 **Estado:** Revisar en la pestaña Actions de GitHub
- 📰 **Resultados:** Ver en redjudicial.cl/noticias.html
- ⏰ **Frecuencia:** Cada 30 minutos automáticamente

## **✅ SISTEMA COMPLETO**

- 🗄️ **Base de datos:** Supabase configurada
- 🤖 **Scrapers:** Todos funcionando (7 fuentes)
- 🔄 **Automatización:** GitHub Actions cada 30 min
- 🧹 **Limpieza:** Sin duplicados, títulos limpios
- 📝 **Resúmenes:** IA generando resúmenes precisos

**¡El sistema está listo para producción!** 🚀 
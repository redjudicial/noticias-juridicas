# 📋 IMPORTANTE - PROCESO DE CORRECCIÓN NOTICIAS JURÍDICAS

## 🎯 PROBLEMA IDENTIFICADO (28 Jul 2025)

### ❌ Issues encontrados:
1. **Duplicación títulos**: Títulos aparecían repetidos en el contenido
2. **Fechas incorrectas**: Mostraba fecha de scraping (28 jul) en lugar de fecha real
3. **Contenido cortado**: CSS limitaba a 8 líneas con `-webkit-line-clamp`
4. **Frases de cierre indeseadas**: "Acceder al expediente..." y datos de contacto

## 🛠️ SOLUCIONES IMPLEMENTADAS

### 1. **LIMPIEZA DE DATOS EN SUPABASE**
- **Script creado**: `limpiar_y_corregir_noticias.py`
- **Función**: Extraer fechas reales del contenido y limpiar duplicación
- **Resultados**: 40 noticias corregidas de 145 total
- **Fechas corregidas**: De "2025-07-28" a fechas reales (ej: "2025-06-13")

### 2. **CORRECCIÓN CSS FRONTEND**
```css
/* ANTES - Limitaba contenido */
.noticia-resumen p {
    display: -webkit-box;
    -webkit-line-clamp: 8;  /* ← CORTABA TEXTO */
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* DESPUÉS - Contenido completo */
.noticia-resumen p {
    margin: 0;
    line-height: 1.6;
    color: var(--text-secondary);
    /* Removido el corte de líneas para mostrar resumen completo */
}
```

### 3. **RESÚMENES EJECUTIVOS MEJORADOS**
- **Script**: `generar_resumenes_ejecutivos.py`
- **Modelo**: Cambio de GPT-4 a GPT-3.5 Turbo (optimización costos)
- **Prompt mejorado**: 6 líneas, núcleo de la noticia, complementa título
- **Columna**: `resumen_ejecutivo` en Supabase

## 📂 ARQUITECTURA DE ARCHIVOS

### **Repositorios:**
- **`/noticias`**: Desarrollo backend, scrapers, scripts
- **`/landing`**: Frontend producción (www.redjudicial.cl)

### **Archivos clave modificados:**
```
/landing/
├── noticias.html (v=20250729-03-NOCACHE)
├── frontend/css/noticias.css (sin line-clamp)
├── frontend/js/noticias.js (fechas corregidas)
└── .github/workflows/ (GitHub Actions NO funciona)

/noticias/
├── limpiar_y_corregir_noticias.py
├── generar_resumenes_ejecutivos.py
├── backend/processors/content_processor.py
└── backend/database/supabase_client.py
```

## 🚀 PROCESO DE DEPLOYMENT

### **❌ GitHub Actions Roto**
- GitHub Actions del repo `sitioweb` NO despliega automáticamente
- Requiere deployment manual SCP

### **✅ Deployment Manual (SCP)**
```bash
# Transferir archivos al servidor AWS Lightsail
scp -i ~/.ssh/LightsailDefaultKey-us-east-1.pem noticias.html bitnami@23.22.241.121:/opt/bitnami/wordpress/
scp -i ~/.ssh/LightsailDefaultKey-us-east-1.pem frontend/css/noticias.css bitnami@23.22.241.121:/opt/bitnami/wordpress/frontend/css/
scp -i ~/.ssh/LightsailDefaultKey-us-east-1.pem frontend/js/noticias.js bitnami@23.22.241.121:/opt/bitnami/wordpress/frontend/js/

# Purgar cache Cloudflare
curl -X POST "https://api.cloudflare.com/client/v4/zones/41a7ba1fa6bff0d03a8ee330f3142e1e/purge_cache" \
     -H "X-Auth-Email: nicolas.barriga@redjudicial.cl" \
     -H "X-Auth-Key: c2c39aca7709ff004afb6f7232d73d70ffbcc" \
     -H "Content-Type: application/json" \
     --data '{"purge_everything":true}'
```

## 🔄 CACHE BUSTING IMPLEMENTADO

### **HTML Headers Anti-Cache:**
```html
<!-- Anti-Cache Headers -->
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
```

### **Versiones archivos:**
- CSS: `v=20250729-03-NOCACHE`
- JS: `v=20250729-03-NOCACHE`

## 📊 RESULTADOS OBTENIDOS

### **✅ Éxitos:**
1. **145 noticias procesadas**, 40 corregidas
2. **Resúmenes ejecutivos** de 6 líneas implementados
3. **Fechas reales** extraídas y corregidas
4. **Contenido completo** visible (sin cortes)
5. **Títulos limpios** sin duplicación

### **❌ Pendientes:**
1. **Limpiar frases de cierre** en contenido
2. **Verificar deployment** en incógnito
3. **Arreglar GitHub Actions** para deployment automático

## 🚨 NOTAS CRÍTICAS

### **Repositorio Correcto:**
- **SIEMPRE trabajar en `/landing`** para cambios frontend
- **NUNCA en `/noticias`** para producción

### **Deployment:**
- **GitHub Actions roto** - usar SCP manual
- **Cache agresivo** - siempre purgar Cloudflare
- **Versiones** - incrementar en cada cambio

### **Database:**
- **Tabla**: `noticias_juridicas` en Supabase
- **Columna resumen**: `resumen_ejecutivo` (no `resumen`)
- **Anti-duplicados**: Por `url_origen`

---
**Fecha actualización**: 29 Jul 2025  
**Estado**: ✅ Funcional con deployment manual  
**Próximo**: Limpiar frases de cierre 
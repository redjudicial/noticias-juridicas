# 📰 Sistema de Noticias Jurídicas - Red Judicial

Sistema automatizado para la recolección, procesamiento y presentación de noticias jurídicas de fuentes oficiales chilenas.

## 🚀 Características

- **10 fuentes oficiales** de noticias jurídicas
- **Scraping automático** cada 30 minutos
- **Resúmenes ejecutivos** generados con IA
- **Metadata completa** para análisis cruzado
- **Frontend profesional** integrado con Red Judicial
- **Base de datos Supabase** optimizada

## 📊 Fuentes Implementadas

1. **Poder Judicial** - Noticias oficiales del PJ
2. **Ministerio de Justicia** - Comunicaciones ministeriales
3. **Defensoría Penal Pública** - Noticias DPP
4. **Contraloría General** - Información de control
5. **Tribunal de Propiedad Industrial** - Noticias TDPI
6. **Comisión Defensa Libre Competencia** - Información CDE
7. **Tribunal Defensa Libre Competencia** - Noticias TDLC
8. **Primer Tribunal Ambiental** - Casos ambientales 1TA
9. **Tercer Tribunal Ambiental** - Casos ambientales 3TA
10. **Tribunal Ambiental General** - Información general ambiental

## 🏗️ Arquitectura

```
noticias/
├── backend/
│   ├── scrapers/fuentes/     # Scrapers por fuente
│   ├── database/            # Cliente Supabase
│   └── processors/          # Procesamiento IA
├── frontend/
│   ├── css/                # Estilos
│   └── js/                 # JavaScript
├── .github/workflows/      # GitHub Actions
└── noticias.html          # Página principal
```

## ⚙️ Configuración

### 1. Variables de Entorno

Crear archivo `APIS_Y_CREDENCIALES.env`:

```bash
SUPABASE_URL=tu_url_supabase
SUPABASE_KEY=tu_key_supabase
OPENAI_API_KEY=tu_key_openai
```

### 2. Dependencias

```bash
pip install -r requirements.txt
```

### 3. Base de Datos

Ejecutar `schema_supabase.sql` en Supabase.

## 🚀 Uso

### Ejecución Manual

```bash
python3 backend/main.py
```

### Automatización

El sistema se ejecuta automáticamente cada 30 minutos via GitHub Actions.

## 📱 Frontend

Acceder a `noticias.html` para ver las noticias con:
- Filtros avanzados
- Búsqueda semántica
- Ordenamiento por fecha
- Resúmenes ejecutivos

## 🤖 IA y Procesamiento

- **Resúmenes ejecutivos** con GPT-4
- **Extracción de metadata** avanzada
- **Clasificación automática** de contenido
- **Análisis de relevancia** jurídica

## 📈 Monitoreo

- Logs automáticos en Supabase
- Métricas de rendimiento
- Alertas de errores
- Dashboard de estadísticas

## 🔧 Desarrollo

### Agregar Nueva Fuente

1. Crear scraper en `backend/scrapers/fuentes/`
2. Configurar en `config.py`
3. Actualizar `__init__.py`
4. Probar con script de test

### Modificar Frontend

- CSS: `frontend/css/noticias.css`
- JS: `frontend/js/noticias.js`
- HTML: `noticias.html`

## 📊 Estadísticas

- **Noticias por día**: ~100-200
- **Fuentes activas**: 10/10
- **Tiempo de ejecución**: 2-3 minutos
- **Tasa de éxito**: >95%

## 🛠️ Tecnologías

- **Backend**: Python 3.11+
- **Base de Datos**: Supabase (PostgreSQL)
- **IA**: OpenAI GPT-4
- **Frontend**: HTML5, CSS3, JavaScript
- **Automatización**: GitHub Actions
- **Scraping**: BeautifulSoup4, Requests

## 📞 Soporte

Para problemas técnicos:
1. Revisar logs en GitHub Actions
2. Verificar configuración de secrets
3. Probar ejecución manual
4. Contactar al equipo de desarrollo

---

**Desarrollado para Red Judicial** 🏛️ 
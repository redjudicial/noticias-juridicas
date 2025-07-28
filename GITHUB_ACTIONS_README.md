# Sistema de Noticias Jurídicas - GitHub Actions

## Configuración Automática

Este repositorio está configurado para ejecutar scraping automático de noticias jurídicas cada 30 minutos.

### Variables de Entorno Requeridas

Configurar en GitHub: Settings > Secrets and variables > Actions

- `SUPABASE_URL`: URL de tu proyecto Supabase
- `SUPABASE_SERVICE_ROLE_KEY`: Service Role Key de Supabase
- `OPENAI_API_KEY`: API Key de OpenAI

### Workflow

El workflow `scraping_automatico.yml` se ejecuta:
- Cada 30 minutos automáticamente
- Manualmente desde la pestaña Actions

### Monitoreo

- Verificar ejecuciones en: Actions > Scraping Automático
- Logs disponibles en cada ejecución
- Notificaciones automáticas de éxito/error

### Última actualización

Configurado el: 2025-07-28 09:33:14
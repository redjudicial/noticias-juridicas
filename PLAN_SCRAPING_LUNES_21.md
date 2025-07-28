# 🚀 Plan de Scraping Automático - Lunes 21 de Julio

## 📅 **Cronograma de Implementación**

### ✅ **Completado (27 de Julio)**
- [x] Sistema de noticias jurídicas implementado
- [x] Base de datos Supabase configurada
- [x] Interfaz web funcional con búsqueda y filtros
- [x] Scripts de control creados
- [x] Sistema de logs configurado

### 🔄 **Lunes 21 de Julio - 9:00 AM**
- [ ] Activar scraping automático
- [ ] Monitorear primera ejecución
- [ ] Verificar logs y métricas

---

## 🎯 **Configuración del Sistema**

### ⏰ **Programación**
- **Inicio**: Lunes 21 de Julio, 9:00 AM
- **Intervalo**: Cada 15 minutos
- **Duración**: Continuo (24/7)
- **Fuentes**: 8 fuentes oficiales chilenas

### 📊 **Fuentes Configuradas**
1. **Poder Judicial** - Scraper web
2. **Tribunal Constitucional** - Scraper web
3. **Ministerio de Justicia** - RSS feed
4. **Fiscalía** - RSS feed
5. **Defensoría Penal Pública** - Scraper web
6. **Contraloría** - RSS feed
7. **Consejo de Defensa del Estado** - RSS feed
8. **Diario Oficial** - Scraper web

---

## 🔧 **Comandos de Control**

### 🚀 **Iniciar Scraping Automático**
```bash
./iniciar_scraping.sh
```

### 📊 **Monitorear en Tiempo Real**
```bash
tail -f scraping.log
```

### 🛑 **Detener Scraping**
```bash
./detener_scraping.sh
```

### 📈 **Ver Estadísticas**
```bash
python3 test_sistema.py
```

---

## 📋 **Checklist para el Lunes 21**

### ⏰ **9:00 AM - Inicio**
- [ ] Ejecutar: `./iniciar_scraping.sh`
- [ ] Verificar que el proceso se inició correctamente
- [ ] Revisar logs iniciales: `tail -f scraping.log`

### ⏰ **9:15 AM - Primera Verificación**
- [ ] Verificar que se ejecutó el primer scraping
- [ ] Revisar noticias nuevas en la base de datos
- [ ] Comprobar que la página web muestra las noticias

### ⏰ **9:30 AM - Segunda Verificación**
- [ ] Verificar segunda ejecución automática
- [ ] Revisar métricas de rendimiento
- [ ] Comprobar logs de errores (si los hay)

### 📊 **Monitoreo Continuo**
- [ ] Revisar logs cada hora
- [ ] Verificar noticias nuevas en la web
- [ ] Monitorear uso de recursos del sistema

---

## 📊 **Métricas a Monitorear**

### 📈 **Rendimiento**
- **Noticias por fuente**: Cuántas noticias se extraen de cada fuente
- **Tiempo de ejecución**: Duración de cada ciclo de scraping
- **Tasa de éxito**: Porcentaje de fuentes que responden correctamente
- **Errores**: Tipos y frecuencia de errores

### 📰 **Contenido**
- **Noticias nuevas**: Cantidad de noticias nuevas por día
- **Duplicados**: Noticias que ya existen en la base de datos
- **Categorías**: Distribución de noticias por categoría
- **Fuentes activas**: Qué fuentes están funcionando correctamente

### 🔍 **Calidad**
- **Resúmenes generados**: Cuántos resúmenes se generan con IA
- **Contenido completo**: Porcentaje de noticias con contenido completo
- **Enlaces válidos**: URLs que funcionan correctamente

---

## 🚨 **Solución de Problemas**

### ❌ **Si el scraping no inicia**
```bash
# Verificar que el proceso esté ejecutándose
ps aux | grep python3

# Verificar logs
cat scraping.log

# Reiniciar si es necesario
./detener_scraping.sh
./iniciar_scraping.sh
```

### ❌ **Si no hay noticias nuevas**
```bash
# Verificar conexión a Supabase
python3 test_sistema.py

# Ejecutar scraping manual
python3 backend/main.py --once

# Revisar logs de errores
grep "ERROR" scraping.log
```

### ❌ **Si la página web no carga**
```bash
# Verificar que la página funcione
open noticias.html

# Verificar conexión a la base de datos
python3 test_sistema.py
```

---

## 📞 **Contacto y Soporte**

### 🔧 **Comandos de Diagnóstico**
```bash
# Estado del sistema
python3 test_sistema.py

# Logs recientes
tail -20 scraping.log

# Estadísticas de la base de datos
python3 -c "
from backend.database.supabase_client import SupabaseClient
import os
from dotenv import load_dotenv
load_dotenv('APIS_Y_CREDENCIALES.env')
client = SupabaseClient(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))
print(f'Total noticias: {client.count_noticias()}')
print(f'Fuentes activas: {len(client.get_fuentes_activas())}')
"
```

### 📊 **URLs Importantes**
- **Página de Noticias**: `noticias.html`
- **Logs del Sistema**: `scraping.log`
- **Base de Datos**: Supabase Dashboard

---

## 🎉 **Éxito Esperado**

### 📈 **Después de 24 horas**
- **50-100 noticias nuevas** en la base de datos
- **8 fuentes funcionando** correctamente
- **Resúmenes generados** para todas las noticias
- **Página web actualizada** automáticamente

### 📈 **Después de 1 semana**
- **500-1000 noticias** en la base de datos
- **Sistema estable** funcionando 24/7
- **Métricas optimizadas** y sin errores
- **Contenido de calidad** para Red Judicial

---

**Estado**: ✅ **SISTEMA LISTO PARA PRODUCCIÓN**

*Preparado para activación: Lunes 21 de Julio, 9:00 AM* 
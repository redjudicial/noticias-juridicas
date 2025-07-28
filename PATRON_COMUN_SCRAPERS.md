# 🎯 PATRÓN COMÚN DE DATOS PARA FRONTEND UNIFICADO

## 🎯 **PROBLEMA RESUELTO**

Cada scraper es específico para su fuente, pero **todos generan el mismo formato de datos** para garantizar un **frontend unificado** con información consistente.

---

## ✅ **SOLUCIÓN IMPLEMENTADA**

### **Esquema de Datos Estandarizado**

```python
@dataclass
class NoticiaEstandarizada:
    """Esquema común que todos los scrapers deben generar"""
    
    # ========================================
    # DATOS BÁSICOS (OBLIGATORIOS)
    # ========================================
    titulo: str
    titulo_original: str
    cuerpo_completo: str
    fecha_publicacion: datetime
    fuente: str  # Código de la fuente
    fuente_nombre_completo: str
    url_origen: str
    
    # ========================================
    # CLASIFICACIÓN ESTANDARIZADA
    # ========================================
    categoria: Optional[Categoria] = None  # FALLOS, ACTIVIDADES, etc.
    jurisdiccion: Optional[Jurisdiccion] = None  # PENAL, CIVIL, etc.
    tipo_documento: Optional[TipoDocumento] = None  # FALLO, RESOLUCION, etc.
    
    # ========================================
    # INFORMACIÓN LEGAL ESPECÍFICA
    # ========================================
    tribunal_organismo: Optional[str] = None
    numero_causa: Optional[str] = None
    rol_causa: Optional[str] = None
    
    # ========================================
    # METADATOS TÉCNICOS
    # ========================================
    hash_contenido: Optional[str] = None  # Detección de duplicados
    fecha_extraccion: Optional[datetime] = None
    version_scraper: Optional[str] = None
```

---

## 🏗️ **ARQUITECTURA DEL PATRÓN**

### **1. Scrapers Específicos por Fuente**
```python
class PoderJudicialScraperV2(BaseScraper):
    """Scraper específico para el Poder Judicial"""
    
    def _extract_info_legal_poder_judicial(self, soup, contenido):
        # Lógica específica del Poder Judicial
        return {
            'jurisdiccion': Jurisdiccion.PENAL,
            'tipo_documento': TipoDocumento.FALLO,
            'categoria': Categoria.FALLOS,
            'tribunal_organismo': 'Corte Suprema'
        }

class MinisterioJusticiaScraper(BaseScraper):
    """Scraper específico para el Ministerio de Justicia"""
    
    def _extract_info_legal_ministerio(self, soup, contenido):
        # Lógica específica del Ministerio
        return {
            'jurisdiccion': Jurisdiccion.GENERAL,
            'tipo_documento': TipoDocumento.COMUNICADO,
            'categoria': Categoria.COMUNICADOS,
            'tribunal_organismo': 'Ministerio de Justicia'
        }
```

### **2. Clase Base Común**
```python
class BaseScraper(ABC):
    """Clase base que garantiza el patrón común"""
    
    def _crear_noticia_estandarizada(self, **kwargs):
        """Método helper para crear noticias estandarizadas"""
        return crear_noticia_estandarizada(**kwargs)
    
    def _validar_noticia(self, noticia):
        """Validar que cumple con el esquema mínimo"""
        return validar_noticia_estandarizada(noticia)
```

### **3. Normalización Automática**
```python
class DataNormalizer:
    """Normaliza datos de diferentes fuentes al esquema común"""
    
    @staticmethod
    def normalize_categoria(categoria_raw: str) -> Optional[Categoria]:
        # Convierte "fallo", "sentencia" → Categoria.FALLOS
    
    @staticmethod
    def normalize_jurisdiccion(jurisdiccion_raw: str) -> Optional[Jurisdiccion]:
        # Convierte "penal", "criminal" → Jurisdiccion.PENAL
    
    @staticmethod
    def extract_palabras_clave(texto: str) -> List[str]:
        # Extrae palabras clave automáticamente
```

---

## 🎯 **BENEFICIOS DEL PATRÓN COMÚN**

### **✅ Frontend Unificado**
- **Una sola interfaz** para todas las fuentes
- **Filtros consistentes** (categoría, jurisdicción, tipo)
- **Búsqueda unificada** en todos los campos
- **Diseño uniforme** de tarjetas de noticias

### **✅ Datos Consistentes en Supabase**
```sql
-- Todas las noticias tienen la misma estructura
SELECT 
    titulo,
    categoria,           -- Enum estandarizado
    jurisdiccion,        -- Enum estandarizado
    tipo_documento,      -- Enum estandarizado
    tribunal_organismo,
    numero_causa,
    hash_contenido       -- Detección de duplicados
FROM noticias_juridicas
WHERE categoria = 'fallos' 
  AND jurisdiccion = 'penal';
```

### **✅ Clasificación Automática**
- **Categorías estandarizadas**: FALLOS, ACTIVIDADES, COMUNICADOS, etc.
- **Jurisdicciones estandarizadas**: PENAL, CIVIL, LABORAL, etc.
- **Tipos de documento estandarizados**: FALLO, RESOLUCION, COMUNICADO, etc.
- **Extracción automática** de palabras clave

### **✅ Detección de Duplicados**
- **Hash único** por noticia basado en contenido
- **Prevención** de noticias duplicadas
- **Actualización** de noticias existentes

---

## 📊 **FLUJO DE DATOS ESTANDARIZADO**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FUENTE WEB    │    │  SCRAPER        │    │  SUPABASE       │
│                 │    │  ESPECÍFICO     │    │                 │
│ Poder Judicial  │───▶│ Poder Judicial  │───▶│ noticias_       │
│ Ministerio      │───▶│ Ministerio      │───▶│ juridicas       │
│ Fiscalía        │───▶│ Fiscalía        │───▶│ (formato        │
│ etc.            │    │ etc.            │    │  común)         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  FRONTEND       │
                       │  UNIFICADO      │
                       │                 │
                       │ • Una interfaz  │
                       │ • Filtros       │
                       │ • Búsqueda      │
                       │ • Diseño común  │
                       └─────────────────┘
```

---

## 🔧 **IMPLEMENTACIÓN TÉCNICA**

### **1. Enums Estandarizados**
```python
class Categoria(Enum):
    FALLOS = "fallos"
    ACTIVIDADES = "actividades"
    COMUNICADOS = "comunicados"
    NOTICIAS = "noticias"
    REFORMAS = "reformas"
    # ...

class Jurisdiccion(Enum):
    PENAL = "penal"
    CIVIL = "civil"
    FAMILIA = "familia"
    LABORAL = "laboral"
    # ...

class TipoDocumento(Enum):
    FALLO = "fallo"
    RESOLUCION = "resolucion"
    COMUNICADO = "comunicado"
    # ...
```

### **2. Validación Automática**
```python
def validar_noticia_estandarizada(noticia: NoticiaEstandarizada) -> bool:
    """Validar que la noticia cumple con el esquema mínimo"""
    required_fields = [
        'titulo', 'titulo_original', 'cuerpo_completo', 
        'fecha_publicacion', 'fuente', 'fuente_nombre_completo', 'url_origen'
    ]
    
    for field_name in required_fields:
        value = getattr(noticia, field_name)
        if not value:
            return False
    
    return True
```

### **3. Conversión a Supabase**
```python
def to_dict(self) -> Dict[str, Any]:
    """Convertir a diccionario para Supabase"""
    return {
        'titulo': self.titulo,
        'categoria': self.categoria.value if self.categoria else None,
        'jurisdiccion': self.jurisdiccion.value if self.jurisdiccion else None,
        'tipo_documento': self.tipo_documento.value if self.tipo_documento else None,
        'hash_contenido': self.hash_contenido,
        # ... todos los campos
    }
```

---

## 🎉 **RESULTADOS OBTENIDOS**

### **✅ Funcionamiento Verificado**
- **Esquema estandarizado** implementado y probado
- **Scraper del Poder Judicial** migrado al nuevo patrón
- **Validación automática** funcionando
- **Normalización de datos** operativa
- **Conversión a Supabase** exitosa

### **📊 Datos de Prueba**
```
✅ Noticia creada: Corte Suprema confirma sentencia en caso de corrupción
   Hash: f6f67637817a513d78cded2f7d5d1dbe
   Categoría: Categoria.FALLOS
   Jurisdicción: Jurisdiccion.PENAL
   Tipo: TipoDocumento.FALLO
   Válida: True
   Diccionario: 28 campos
```

### **🔧 Próximos Pasos**
1. **Migrar todos los scrapers** al nuevo patrón
2. **Implementar scrapers específicos** para fuentes faltantes
3. **Actualizar frontend** para usar los enums estandarizados
4. **Optimizar consultas** de Supabase con el nuevo esquema

---

## 📝 **CONCLUSIÓN**

El **patrón común de datos** ha sido **exitosamente implementado** y proporciona:

- **✅ Frontend unificado** garantizado
- **✅ Datos consistentes** en Supabase
- **✅ Clasificación automática** estandarizada
- **✅ Detección de duplicados** automática
- **✅ Escalabilidad** para nuevas fuentes
- **✅ Mantenimiento simplificado**

**Cada scraper es específico para su fuente, pero todos terminan generando el mismo formato de datos para un frontend unificado.** 🎯

---

*Documento generado el 27 de julio de 2025*
*Patrón Común de Datos - Sistema de Noticias Jurídicas* 
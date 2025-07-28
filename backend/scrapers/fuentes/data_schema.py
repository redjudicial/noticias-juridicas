#!/usr/bin/env python3
"""
Esquema de datos estandarizado para noticias jurídicas
Define las estructuras de datos comunes para todos los scrapers
"""

import re
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

class Categoria(Enum):
    """Categorías de noticias jurídicas"""
    TRIBUNAL = "tribunal"
    MINISTERIO = "ministerio"
    FISCALIA = "fiscalia"
    DEFENSORIA = "defensoria"
    CONTRALORIA = "contraloria"
    ORGANISMO = "organismo"
    LEGISLACION = "legislacion"
    JURISPRUDENCIA = "jurisprudencia"
    ADMINISTRATIVO = "administrativo"
    PENAL = "penal"
    CIVIL = "civil"
    LABORAL = "laboral"
    AMBIENTAL = "ambiental"
    CONSTITUCIONAL = "constitucional"
    COMERCIAL = "comercial"
    TRIBUTARIO = "tributario"
    OTRO = "otro"

class Jurisdiccion(Enum):
    """Jurisdicciones del sistema judicial"""
    NACIONAL = "nacional"
    REGIONAL = "regional"
    LOCAL = "local"
    INTERNACIONAL = "internacional"

class TipoDocumento(Enum):
    """Tipos de documentos jurídicos"""
    NOTICIA = "noticia"
    SENTENCIA = "sentencia"
    RESOLUCION = "resolucion"
    ACUERDO = "acuerdo"
    DICTAMEN = "dictamen"
    INFORME = "informe"
    CIRCULAR = "circular"
    INSTRUCTIVO = "instructivo"
    DECRETO = "decreto"
    LEY = "ley"
    REGLAMENTO = "reglamento"
    AUDIENCIA = "audiencia"
    CONCURSO = "concurso"
    LICITACION = "licitacion"
    OTRO = "otro"

@dataclass
class MetadataNoticia:
    """Metadata adicional de la noticia"""
    # Información temporal
    fecha_creacion: Optional[datetime] = None
    fecha_modificacion: Optional[datetime] = None
    fecha_vencimiento: Optional[datetime] = None
    
    # Información de autoría
    autor_nombre: Optional[str] = None
    autor_cargo: Optional[str] = None
    autor_email: Optional[str] = None
    autor_departamento: Optional[str] = None
    
    # Información geográfica
    region: Optional[str] = None
    comuna: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    
    # Información de causa
    numero_causa: Optional[str] = None
    rol_causa: Optional[str] = None
    tribunal_instancia: Optional[str] = None
    ministro_relator: Optional[str] = None
    abogado_demandante: Optional[str] = None
    abogado_demandado: Optional[str] = None
    
    # Información de contenido
    numero_paginas: Optional[int] = None
    numero_palabras: Optional[int] = None
    idioma: Optional[str] = None
    formato_original: Optional[str] = None
    
    # Información técnica
    scraper_version: Optional[str] = None
    fecha_extraccion: Optional[datetime] = None
    url_original: Optional[str] = None
    headers_request: Optional[Dict] = None
    status_code: Optional[int] = None
    
    # Información de relevancia
    relevancia_juridica: Optional[int] = None
    impacto_publico: Optional[int] = None
    urgencia: Optional[str] = None
    confidencialidad: Optional[str] = None
    
    # Información de categorización
    subcategoria: Optional[str] = None
    etiquetas: List[str] = field(default_factory=list)
    temas_relacionados: List[str] = field(default_factory=list)
    
    # Información de archivos
    archivos_adjuntos: List[str] = field(default_factory=list)
    imagenes: List[str] = field(default_factory=list)
    documentos_pdf: List[str] = field(default_factory=list)
    
    # Información de enlaces
    enlaces_relacionados: List[str] = field(default_factory=list)
    referencias_bibliograficas: List[str] = field(default_factory=list)
    
    # Información de contacto
    contacto_nombre: Optional[str] = None
    contacto_email: Optional[str] = None
    contacto_telefono: Optional[str] = None
    
    # Información de eventos
    fecha_evento: Optional[datetime] = None
    lugar_evento: Optional[str] = None
    tipo_evento: Optional[str] = None
    
    # Información de seguimiento
    estado_seguimiento: Optional[str] = None
    proxima_audiencia: Optional[datetime] = None
    plazo_vencimiento: Optional[datetime] = None

@dataclass
class NoticiaEstandarizada:
    """Noticia estandarizada para almacenamiento en base de datos"""
    # Información básica (requerida)
    titulo: str
    cuerpo_completo: str
    fecha_publicacion: datetime
    fuente: str
    url_origen: str
    categoria: Categoria
    jurisdiccion: Jurisdiccion
    tipo_documento: TipoDocumento
    
    # Información básica (opcional)
    titulo_original: Optional[str] = None
    subtitulo: Optional[str] = None
    resumen_ejecutivo: Optional[str] = None
    extracto_fuente: Optional[str] = None
    
    # Información temporal
    fecha_actualizacion: Optional[datetime] = None
    fecha_scraping: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Información de fuente
    fuente_nombre_completo: Optional[str] = None
    url_imagen: Optional[str] = None
    tribunal_organismo: Optional[str] = None
    
    # Palabras clave y etiquetas
    palabras_clave: List[str] = field(default_factory=list)
    etiquetas: List[str] = field(default_factory=list)
    
    # Metadata completa
    metadata: MetadataNoticia = field(default_factory=MetadataNoticia)
    
    # Campos para IA
    resumen_juridico: Optional[str] = None
    embedding_vector: Optional[List[float]] = None
    
    # Campos de control
    hash_contenido: Optional[str] = None
    version: int = 1
    es_actualizacion: bool = False
    
    def __post_init__(self):
        """Validaciones y procesamiento post-inicialización"""
        # Asegurar que el título esté completo
        if self.titulo and len(self.titulo.strip()) > 0:
            self.titulo = self.titulo.strip()
            # Si no hay título original, usar el título como original
            if not self.titulo_original:
                self.titulo_original = self.titulo
        
        # Procesar fecha de publicación
        if isinstance(self.fecha_publicacion, str):
            self.fecha_publicacion = self._parse_fecha(self.fecha_publicacion)
        
        # Generar hash si no existe
        if not self.hash_contenido:
            self.hash_contenido = self._generar_hash()
        
        # Asegurar que las listas no sean None
        if self.palabras_clave is None:
            self.palabras_clave = []
        if self.etiquetas is None:
            self.etiquetas = []
    
    def _parse_fecha(self, fecha_str: str) -> datetime:
        """Parsear fecha en múltiples formatos"""
        if not fecha_str:
            return datetime.now(timezone.utc)
        
        # Formato: DD/MM/YYYY HH:MM:SS
        if re.match(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}', fecha_str):
            return datetime.strptime(fecha_str, '%d/%m/%Y %H:%M:%S').replace(tzinfo=timezone.utc)
        
        # Formato: DD/MM/YYYY HH:MM
        if re.match(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}', fecha_str):
            return datetime.strptime(fecha_str, '%d/%m/%Y %H:%M').replace(tzinfo=timezone.utc)
        
        # Formato: DD/MM/YYYY
        if re.match(r'\d{2}/\d{2}/\d{4}', fecha_str):
            return datetime.strptime(fecha_str, '%d/%m/%Y').replace(tzinfo=timezone.utc)
        
        # Formato: YYYY-MM-DD HH:MM:SS
        if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', fecha_str):
            return datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        
        # Formato: YYYY-MM-DD
        if re.match(r'\d{4}-\d{2}-\d{2}', fecha_str):
            return datetime.strptime(fecha_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        
        # Si no se puede parsear, usar fecha actual
        return datetime.now(timezone.utc)
    
    def _generar_hash(self) -> str:
        """Generar hash único del contenido"""
        import hashlib
        contenido = f"{self.titulo}{self.cuerpo_completo}{self.url_origen}"
        return hashlib.md5(contenido.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para almacenamiento en base de datos"""
        return {
            'titulo': self.titulo,
            'titulo_original': self.titulo_original,
            'subtitulo': self.subtitulo,
            'resumen_ejecutivo': self.resumen_ejecutivo,
            'cuerpo_completo': self.cuerpo_completo,
            'extracto_fuente': self.extracto_fuente,
            'fecha_publicacion': self.fecha_publicacion.isoformat(),
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'fecha_scraping': self.fecha_scraping.isoformat(),
            'fuente': self.fuente,
            'fuente_nombre_completo': self.fuente_nombre_completo,
            'url_origen': self.url_origen,
            'url_imagen': self.url_imagen,
            'categoria': self.categoria.value,
            'jurisdiccion': self.jurisdiccion.value,
            'tipo_documento': self.tipo_documento.value,
            'tribunal_organismo': self.tribunal_organismo,
            'palabras_clave': self.palabras_clave,
            'etiquetas': self.etiquetas,
            'resumen_juridico': self.resumen_juridico,
            'hash_contenido': self.hash_contenido,
            'version': self.version,
            'es_actualizacion': self.es_actualizacion,
            # Metadata expandida
            'autor': self.metadata.autor_nombre,
            'autor_cargo': self.metadata.autor_cargo,
            'numero_causa': self.metadata.numero_causa,
            'rol_causa': self.metadata.rol_causa,
            'region': self.metadata.region,
            'relevancia_juridica': self.metadata.relevancia_juridica,
            'impacto_publico': self.metadata.impacto_publico,
            'subcategoria': self.metadata.subcategoria,
            'scraper_version': self.metadata.scraper_version,
            'fecha_extraccion': self.metadata.fecha_extraccion.isoformat() if self.metadata.fecha_extraccion else None,
            'url_original': self.metadata.url_original,
            'status_code': self.metadata.status_code,
            'numero_palabras': self.metadata.numero_palabras,
            'idioma': self.metadata.idioma,
            'urgencia': self.metadata.urgencia,
            'confidencialidad': self.metadata.confidencialidad,
            'temas_relacionados': self.metadata.temas_relacionados,
            'archivos_adjuntos': self.metadata.archivos_adjuntos,
            'imagenes': self.metadata.imagenes,
            'documentos_pdf': self.metadata.documentos_pdf,
            'enlaces_relacionados': self.metadata.enlaces_relacionados,
            'referencias_bibliograficas': self.metadata.referencias_bibliograficas,
            'contacto_nombre': self.metadata.contacto_nombre,
            'contacto_email': self.metadata.contacto_email,
            'contacto_telefono': self.metadata.contacto_telefono,
            'fecha_evento': self.metadata.fecha_evento.isoformat() if self.metadata.fecha_evento else None,
            'lugar_evento': self.metadata.lugar_evento,
            'tipo_evento': self.metadata.tipo_evento,
            'estado_seguimiento': self.metadata.estado_seguimiento,
            'proxima_audiencia': self.metadata.proxima_audiencia.isoformat() if self.metadata.proxima_audiencia else None,
            'plazo_vencimiento': self.metadata.plazo_vencimiento.isoformat() if self.metadata.plazo_vencimiento else None
        }

class DataNormalizer:
    """Normalizador de datos para estandarizar información de diferentes fuentes"""
    
    @staticmethod
    def normalizar_fecha(fecha_str: str) -> datetime:
        """Normalizar fecha en múltiples formatos"""
        if not fecha_str:
            return datetime.now(timezone.utc)
        
        # Formato: DD/MM/YYYY HH:MM:SS
        if re.match(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}', fecha_str):
            return datetime.strptime(fecha_str, '%d/%m/%Y %H:%M:%S').replace(tzinfo=timezone.utc)
        
        # Formato: DD/MM/YYYY HH:MM
        if re.match(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}', fecha_str):
            return datetime.strptime(fecha_str, '%d/%m/%Y %H:%M').replace(tzinfo=timezone.utc)
        
        # Formato: DD/MM/YYYY
        if re.match(r'\d{2}/\d{2}/\d{4}', fecha_str):
            return datetime.strptime(fecha_str, '%d/%m/%Y').replace(tzinfo=timezone.utc)
        
        # Formato: YYYY-MM-DD HH:MM:SS
        if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', fecha_str):
            return datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        
        # Formato: YYYY-MM-DD
        if re.match(r'\d{4}-\d{2}-\d{2}', fecha_str):
            return datetime.strptime(fecha_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        
        # Si no se puede parsear, usar fecha actual
        return datetime.now(timezone.utc)
    
    @staticmethod
    def extraer_metadata_avanzada(texto: str, url: str = None) -> MetadataNoticia:
        """Extraer metadata avanzada del texto y URL"""
        metadata = MetadataNoticia()
        
        # Extraer información de causa
        patrones_causa = [
            r'Rol\s+([A-Z]?\s*\d+-\d+)',
            r'Causa\s+([A-Z]?\s*\d+-\d+)',
            r'R\.\s*([A-Z]?\s*\d+-\d+)',
            r'C\.\s*([A-Z]?\s*\d+-\d+)'
        ]
        
        for patron in patrones_causa:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                metadata.rol_causa = match.group(1).strip()
                break
        
        # Extraer información de tribunal
        tribunales = [
            'Corte Suprema', 'Corte de Apelaciones', 'Juzgado Civil', 'Juzgado Penal',
            'Tribunal Ambiental', 'Tribunal de Defensa de la Libre Competencia',
            'Contraloría', 'Fiscalía', 'Defensoría'
        ]
        
        for tribunal in tribunales:
            if tribunal.lower() in texto.lower():
                metadata.tribunal_instancia = tribunal
                break
        
        # Extraer información geográfica
        regiones = [
            'Arica y Parinacota', 'Tarapacá', 'Antofagasta', 'Atacama', 'Coquimbo',
            'Valparaíso', 'Metropolitana', 'O\'Higgins', 'Maule', 'Ñuble',
            'Biobío', 'La Araucanía', 'Los Ríos', 'Los Lagos', 'Aysén', 'Magallanes'
        ]
        
        for region in regiones:
            if region.lower() in texto.lower():
                metadata.region = region
                break
        
        # Contar palabras
        metadata.numero_palabras = len(texto.split())
        
        # Detectar idioma (simplificado)
        metadata.idioma = 'es'  # Por defecto español
        
        # Extraer fechas de eventos
        patrones_fecha = [
            r'(\d{2}/\d{2}/\d{4})\s+(?:a las\s+)?(\d{2}:\d{2})',
            r'(\d{2}/\d{2}/\d{4})',
            r'(\d{4}-\d{2}-\d{2})'
        ]
        
        for patron in patrones_fecha:
            match = re.search(patron, texto)
            if match:
                try:
                    if len(match.groups()) == 2:
                        fecha_str = f"{match.group(1)} {match.group(2)}"
                        metadata.fecha_evento = DataNormalizer.normalizar_fecha(fecha_str)
                    else:
                        metadata.fecha_evento = DataNormalizer.normalizar_fecha(match.group(1))
                    break
                except:
                    continue
        
        return metadata
    
    @staticmethod
    def limpiar_titulo(titulo: str) -> str:
        """Limpiar y normalizar título"""
        if not titulo:
            return ""
        
        # Remover caracteres especiales al inicio/final
        titulo = titulo.strip()
        
        # Remover múltiples espacios
        titulo = re.sub(r'\s+', ' ', titulo)
        
        # Asegurar que termine con punto si es una oración completa
        if titulo and not titulo.endswith(('.', '!', '?')):
            # Solo agregar punto si parece ser una oración completa
            if len(titulo) > 20 and not titulo.endswith('...'):
                titulo += '.'
        
        return titulo 

def crear_noticia_estandarizada(
    titulo: str,
    cuerpo_completo: str,
    fecha_publicacion: datetime,
    fuente: str,
    url_origen: str,
    categoria: Categoria = Categoria.OTRO,
    jurisdiccion: Jurisdiccion = Jurisdiccion.NACIONAL,
    tipo_documento: TipoDocumento = TipoDocumento.NOTICIA,
    **kwargs
) -> NoticiaEstandarizada:
    """
    Función helper para crear una NoticiaEstandarizada con valores por defecto
    
    Args:
        titulo: Título de la noticia
        cuerpo_completo: Contenido completo de la noticia
        fecha_publicacion: Fecha de publicación
        fuente: Nombre de la fuente
        url_origen: URL de origen
        categoria: Categoría de la noticia
        jurisdiccion: Jurisdicción
        tipo_documento: Tipo de documento
        **kwargs: Argumentos adicionales para campos opcionales
    
    Returns:
        NoticiaEstandarizada: Instancia de noticia estandarizada
    """
    # Extraer metadata del contenido
    metadata = DataNormalizer.extraer_metadata_avanzada(cuerpo_completo, url_origen)
    
    # Limpiar título
    titulo_limpio = DataNormalizer.limpiar_titulo(titulo)
    
    # Crear la noticia estandarizada
    return NoticiaEstandarizada(
        titulo=titulo_limpio,
        cuerpo_completo=cuerpo_completo,
        fecha_publicacion=fecha_publicacion,
        fuente=fuente,
        url_origen=url_origen,
        categoria=categoria,
        jurisdiccion=jurisdiccion,
        tipo_documento=tipo_documento,
        metadata=metadata,
        **kwargs
    )

def validar_noticia_estandarizada(noticia: NoticiaEstandarizada) -> bool:
    """
    Validar que una noticia estandarizada tenga todos los campos requeridos
    
    Args:
        noticia: Instancia de NoticiaEstandarizada a validar
    
    Returns:
        bool: True si la noticia es válida, False en caso contrario
    """
    try:
        # Validar campos requeridos
        if not noticia.titulo or not noticia.titulo.strip():
            print("❌ Error: Título vacío o nulo")
            return False
        
        if not noticia.cuerpo_completo or not noticia.cuerpo_completo.strip():
            print("❌ Error: Cuerpo completo vacío o nulo")
            return False
        
        if not noticia.fecha_publicacion:
            print("❌ Error: Fecha de publicación nula")
            return False
        
        if not noticia.fuente or not noticia.fuente.strip():
            print("❌ Error: Fuente vacía o nula")
            return False
        
        if not noticia.url_origen or not noticia.url_origen.strip():
            print("❌ Error: URL de origen vacía o nula")
            return False
        
        # Validar que la URL sea válida
        if not noticia.url_origen.startswith(('http://', 'https://')):
            print("❌ Error: URL de origen no válida")
            return False
        
        # Validar longitud mínima del contenido
        if len(noticia.cuerpo_completo.strip()) < 50:
            print("❌ Error: Contenido demasiado corto (mínimo 50 caracteres)")
            return False
        
        # Validar que el título no sea demasiado largo
        if len(noticia.titulo.strip()) > 500:
            print("❌ Error: Título demasiado largo (máximo 500 caracteres)")
            return False
        
        # Validar que la fecha no sea futura (con margen de 1 día)
        from datetime import timedelta
        if noticia.fecha_publicacion > datetime.now(timezone.utc) + timedelta(days=1):
            print("❌ Error: Fecha de publicación en el futuro")
            return False
        
        # Validar que la fecha no sea muy antigua (más de 10 años)
        if noticia.fecha_publicacion < datetime.now(timezone.utc) - timedelta(days=3650):
            print("❌ Error: Fecha de publicación muy antigua")
            return False
        
        print("✅ Noticia válida")
        return True
        
    except Exception as e:
        print(f"❌ Error validando noticia: {e}")
        return False 
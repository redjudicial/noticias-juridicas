#!/usr/bin/env python3
"""
Configuración centralizada para todos los scrapers de noticias jurídicas
"""

# ========================================
# CONFIGURACIÓN GENERAL
# ========================================
SCRAPING_CONFIG = {
    'timeout': 30,
    'max_retries': 3,
    'pause_between_requests': 1,
    'max_noticias_por_fuente': 20,
    'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# ========================================
# CONFIGURACIÓN POR FUENTE
# ========================================

# Poder Judicial
PODER_JUDICIAL_CONFIG = {
    'nombre': 'Poder Judicial de Chile',
    'codigo': 'poder_judicial',
    'url_base': 'https://www.pjud.cl',
    'url_noticias': 'https://www.pjud.cl/prensa-y-comunicaciones/noticias-del-poder-judicial',
    'activo': True,
    'prioridad': 1,
    'palabras_clave': [
        'fiscal', 'corte', 'juzgado', 'tribunal', 'sentencia', 'fallo', 
        'condena', 'prisión', 'acusado', 'imputado', 'sumario', 'querella',
        'liquidación', 'robo', 'abuso', 'violación', 'homicidio', 'alcalde',
        'ejército', 'garantía', 'apelaciones', 'suprema', 'oral', 'penal'
    ],
    'exclusiones': [
        'anterior', 'siguiente', 'última', 'página', 'filtrar', 'inicio',
        'menu', 'portal', 'sistema', 'traducción', 'licitaciones'
    ]
}

# Ministerio de Justicia
MINISTERIO_JUSTICIA_CONFIG = {
    'nombre': 'Ministerio de Justicia de Chile',
    'codigo': 'ministerio_justicia',
    'url_base': 'https://www.minjusticia.gob.cl',
    'url_noticias': 'https://www.minjusticia.gob.cl/category/noticias/',
    'activo': True,
    'prioridad': 1,
    'palabras_clave': [
        'ley', 'proyecto', 'reforma', 'código', 'servicio', 'nacional',
        'defensoría', 'víctimas', 'derechos', 'humanos', 'justicia',
        'penal', 'civil', 'familia', 'adopciones', 'delitos'
    ],
    'exclusiones': [
        'regiones', 'seminarios', 'subsecretario', 'defensoria', 'caj',
        'mediacion', 'transparencia', 'trabaja', 'indicadores', 'lobby'
    ]
}

# Defensoría Penal Pública
DPP_CONFIG = {
    'nombre': 'Defensoría Penal Pública de Chile',
    'codigo': 'dpp',
    'url_base': 'https://www.dpp.cl',
    'url_noticias': 'https://www.dpp.cl/sala_prensa/noticias',
    'activo': True,  # Funcionando
    'prioridad': 2,
    'palabras_clave': [
        'defensa', 'penal', 'pública', 'defensor', 'acusado', 'imputado',
        'proceso', 'penal', 'garantías', 'derechos', 'defensoría'
    ],
    'exclusiones': [
        'inicio', 'menu', 'departamentos', 'unidades', 'regiones'
    ]
}

# Contraloría General de la República
CONTRALORIA_CONFIG = {
    'nombre': 'Contraloría General de la República',
    'codigo': 'contraloria',
    'url_base': 'https://www.contraloria.cl',
    'url_noticias': 'https://www.contraloria.cl/portalweb/web/cgr/noticias',
    'activo': True,  # Funcionando
    'prioridad': 2,
    'palabras_clave': [
        'contraloría', 'contralor', 'auditoría', 'control', 'fiscalización',
        'estado', 'gobierno', 'municipal', 'servicio', 'público', 'cgr'
    ],
    'exclusiones': [
        'inicio', 'menu', 'contacto', 'transparencia'
    ]
}

# Tribunal de Propiedad Industrial
TDPI_CONFIG = {
    'nombre': 'Tribunal de Propiedad Industrial',
    'codigo': 'tdpi',
    'url_base': 'https://www.tdpi.cl',
    'url_noticias': 'https://www.tdpi.cl/category/noticias/',
    'activo': True,  # Funcionando
    'prioridad': 3,
    'palabras_clave': [
        'propiedad', 'industrial', 'patente', 'marca', 'registro',
        'intelectual', 'comercial', 'tdpi', 'tribunal'
    ],
    'exclusiones': [
        'inicio', 'menu', 'contacto', 'transparencia'
    ]
}

# CDE (Comisión de Defensa de la Libre Competencia)
CDE_CONFIG = {
    'nombre': 'Comisión de Defensa de la Libre Competencia',
    'codigo': 'cde',
    'url_base': 'https://www.cde.cl',
    'url_noticias': 'https://www.cde.cl/post-sitemap1.xml',
    'activo': True,  # Funcionando
    'prioridad': 3,
    'palabras_clave': [
        'libre', 'competencia', 'antitrust', 'monopolio', 'oligopolio',
        'mercado', 'empresa', 'comercial', 'económico', 'competitivo'
    ],
    'exclusiones': [
        'inicio', 'menu', 'contacto', 'transparencia'
    ]
}

# Nuevas fuentes de tribunales ambientales y TDLC
TDLC_CONFIG = {
    'nombre': 'Tribunal de Defensa de la Libre Competencia',
    'codigo': 'tdlc',
    'url_base': 'https://www.tdlc.cl',
    'url_noticias': 'https://www.tdlc.cl/noticias/',
    'activo': True,
    'prioridad': 1,
    'palabras_clave': [
        'tdlc', 'libre competencia', 'antimonopolio', 'competencia', 'mercado',
        'fiscalía nacional económica', 'fne', 'decreto ley 211'
    ],
    'categoria': 'TRIBUNAL',
    'jurisdiccion': 'NACIONAL'
}

TRIBUNAL_AMBIENTAL_1TA_CONFIG = {
    'nombre': 'Tribunal Ambiental',
    'codigo': '1ta',
    'url_base': 'https://www.1ta.cl',
    'url_noticias': 'https://www.1ta.cl/category/noticias/',
    'activo': True,
    'prioridad': 2,
    'palabras_clave': [
        '1ta', 'primer tribunal ambiental', 'medio ambiente', 'ambiental',
        'contaminación', 'evaluación ambiental', 'daño ambiental'
    ],
    'categoria': 'TRIBUNAL',
    'jurisdiccion': 'NACIONAL',
    'prefijo': '(1º)'
}

TRIBUNAL_AMBIENTAL_3TA_CONFIG = {
    'nombre': 'Tribunal Ambiental',
    'codigo': '3ta',
    'url_base': 'https://3ta.cl',
    'url_noticias': 'https://3ta.cl/category/noticias/',
    'activo': True,
    'prioridad': 2,
    'palabras_clave': [
        '3ta', 'tercer tribunal ambiental', 'medio ambiente', 'ambiental',
        'contaminación', 'evaluación ambiental', 'daño ambiental'
    ],
    'categoria': 'TRIBUNAL',
    'jurisdiccion': 'NACIONAL',
    'prefijo': '(3º)'
}

TRIBUNAL_AMBIENTAL_GENERAL_CONFIG = {
    'nombre': 'Tribunal Ambiental',
    'codigo': 'tribunal_ambiental',
    'url_base': 'https://tribunalambiental.cl',
    'url_noticias': 'https://tribunalambiental.cl/category/noticias/',
    'activo': True,
    'prioridad': 2,
    'palabras_clave': [
        'tribunal ambiental', 'medio ambiente', 'ambiental', 'contaminación',
        'evaluación ambiental', 'daño ambiental', 'ley 19.300'
    ],
    'categoria': 'TRIBUNAL',
    'jurisdiccion': 'NACIONAL',
    'prefijo': '(2º)'
}

# Servicio de Impuestos Internos
SII_CONFIG = {
    'nombre': 'SII',
    'codigo': 'sii',
    'url_base': 'https://www.sii.cl',
    'url_noticias': 'https://www.sii.cl/noticias/2025/index.html',
    'activo': True,
    'prioridad': 3,
    'palabras_clave': [
        'impuesto', 'tributario', 'fiscal', 'iva', 'renta', 'contribuyente',
        'declaración', 'formulario', 'sii', 'servicio impuestos internos',
        'código tributario', 'evasión', 'fiscalización'
    ],
    'exclusiones': [
        'menú', 'inicio', 'buscar', 'rss', 'formularios', 'trámites'
    ],
    'categoria': 'NORMATIVA',
    'jurisdiccion': 'NACIONAL'
}

# Tribunales Tributarios y Aduaneros
TTA_CONFIG = {
    'nombre': 'TTA',
    'codigo': 'tta',
    'url_base': 'https://www.tta.cl',
    'url_noticias': 'https://www.tta.cl/noticias/',
    'activo': True,
    'prioridad': 3,
    'palabras_clave': [
        'tribunal', 'tributario', 'aduanero', 'impuesto', 'fiscal',
        'tta', 'reclamación', 'resolución', 'aduana'
    ],
    'exclusiones': [
        'menú', 'inicio', 'buscar', 'rss', 'formularios'
    ],
    'categoria': 'TRIBUNAL',
    'jurisdiccion': 'NACIONAL'
}

# Instituto Nacional de Propiedad Industrial
INAPI_CONFIG = {
    'nombre': 'INAPI',
    'codigo': 'inapi',
    'url_base': 'https://www.inapi.cl',
    'url_noticias': 'https://www.inapi.cl/sala-de-prensa/noticias',
    'activo': True,
    'prioridad': 3,
    'palabras_clave': [
        'propiedad industrial', 'patente', 'marca', 'diseño',
        'inapi', 'registro', 'invención', 'innovación'
    ],
    'exclusiones': [
        'menú', 'inicio', 'buscar', 'rss', 'formularios', 'trámites'
    ],
    'categoria': 'NORMATIVA',
    'jurisdiccion': 'NACIONAL'
}

# Dirección del Trabajo
DT_CONFIG = {
    'nombre': 'DT',
    'codigo': 'dt',
    'url_base': 'https://www.dt.gob.cl',
    'url_noticias': 'https://www.dt.gob.cl/portal/1627/w3-propertyvalue-191853.html',
    'activo': True,
    'prioridad': 3,
    'palabras_clave': [
        'trabajo', 'laboral', 'empleador', 'trabajador',
        'inspección', 'fiscalización', 'sindicato', 'contrato'
    ],
    'exclusiones': [
        'menú', 'inicio', 'buscar', 'rss', 'formularios', 'trámites'
    ],
    'categoria': 'NORMATIVA',
    'jurisdiccion': 'NACIONAL'
}

# ========================================
# CONFIGURACIÓN DE TODAS LAS FUENTES
# ========================================
FUENTES_CONFIG = {
    'poder_judicial': PODER_JUDICIAL_CONFIG,
    'ministerio_justicia': MINISTERIO_JUSTICIA_CONFIG,
    'dpp': DPP_CONFIG,
    'contraloria': CONTRALORIA_CONFIG,
    'tdpi': TDPI_CONFIG,
    'cde': CDE_CONFIG,
    'tdlc': TDLC_CONFIG,
    '1ta': TRIBUNAL_AMBIENTAL_1TA_CONFIG,
    '3ta': TRIBUNAL_AMBIENTAL_3TA_CONFIG,
    'tribunal_ambiental': TRIBUNAL_AMBIENTAL_GENERAL_CONFIG,
    'sii': SII_CONFIG,
    'tta': TTA_CONFIG,
    'inapi': INAPI_CONFIG,
    'dt': DT_CONFIG
}

# ========================================
# FUNCIONES DE UTILIDAD
# ========================================

def get_fuentes_activas():
    """Obtener lista de fuentes activas"""
    return {codigo: config for codigo, config in FUENTES_CONFIG.items() if config['activo']}

def get_fuente_config(codigo: str):
    """Obtener configuración de una fuente específica"""
    return FUENTES_CONFIG.get(codigo, {})

def get_fuentes_por_prioridad():
    """Obtener fuentes ordenadas por prioridad"""
    fuentes_activas = get_fuentes_activas()
    return sorted(fuentes_activas.items(), key=lambda x: x[1]['prioridad'])

def is_fuente_activa(codigo: str) -> bool:
    """Verificar si una fuente está activa"""
    config = get_fuente_config(codigo)
    return config.get('activo', False)

def get_fuente_nombre(codigo: str) -> str:
    """Obtener nombre de una fuente"""
    config = get_fuente_config(codigo)
    return config.get('nombre', 'Fuente desconocida')

def get_fuente_url(codigo: str) -> str:
    """Obtener URL de noticias de una fuente"""
    config = get_fuente_config(codigo)
    return config.get('url_noticias', '')

def get_fuente_palabras_clave(codigo: str) -> list:
    """Obtener palabras clave de una fuente"""
    config = get_fuente_config(codigo)
    return config.get('palabras_clave', [])

def get_fuente_exclusiones(codigo: str) -> list:
    """Obtener exclusiones de una fuente"""
    config = get_fuente_config(codigo)
    return config.get('exclusiones', []) 
"""
Módulo principal de scrapers de noticias jurídicas
Organizado por fuentes para mejor mantenimiento
"""

from .config import (
    FUENTES_CONFIG,
    get_fuentes_activas,
    get_fuente_config,
    get_fuentes_por_prioridad,
    is_fuente_activa,
    get_fuente_nombre,
    get_fuente_url,
    get_fuente_palabras_clave,
    get_fuente_exclusiones
)

# Importar scrapers específicos
try:
    from .poder_judicial import PoderJudicialScraper
except ImportError:
    PoderJudicialScraper = None

try:
    from .ministerio_justicia import MinisterioJusticiaScraper
except ImportError:
    MinisterioJusticiaScraper = None

try:
    from .dpp import DPPScraper
except ImportError:
    DPPScraper = None

try:
    from .contraloria import ContraloriaScraper
except ImportError:
    ContraloriaScraper = None

try:
    from .tdpi import TDPScraper
except ImportError:
    TDPScraper = None

try:
    from .cde import CDEScraper
except ImportError:
    CDEScraper = None

# Nuevos scrapers de tribunales ambientales y TDLC
from .tdlc import TDLScraper
from .primer_tribunal_ambiental import PrimerTribunalAmbientalScraper
from .tercer_tribunal_ambiental import TercerTribunalAmbientalScraper
from .tribunal_ambiental import TribunalAmbientalScraper

# Diccionario de scrapers disponibles
SCRAPERS_DISPONIBLES = {
    'poder_judicial': PoderJudicialScraper,
    'ministerio_justicia': MinisterioJusticiaScraper,
    'dpp': DPPScraper,
    'contraloria': ContraloriaScraper,
    'tdpi': TDPScraper,
    'cde': CDEScraper,
    'tdlc': TDLScraper,
    '1ta': PrimerTribunalAmbientalScraper,
    '3ta': TercerTribunalAmbientalScraper,
    'tribunal_ambiental': TribunalAmbientalScraper
}

def get_scraper(fuente: str):
    """Obtener scraper para una fuente específica"""
    return SCRAPERS_DISPONIBLES.get(fuente)

def get_scrapers_activos():
    """Obtener diccionario de scrapers activos"""
    scrapers_activos = {}
    fuentes_activas = get_fuentes_activas()
    
    for codigo, config in fuentes_activas.items():
        scraper_class = get_scraper(codigo)
        if scraper_class:
            scrapers_activos[codigo] = scraper_class
    
    return scrapers_activos

def listar_fuentes_disponibles():
    """Listar todas las fuentes disponibles con su estado"""
    print("📰 FUENTES DE NOTICIAS JURÍDICAS")
    print("=" * 50)
    
    for codigo, config in FUENTES_CONFIG.items():
        estado = "✅ ACTIVA" if config['activo'] else "🔧 EN DESARROLLO"
        scraper_disponible = "✅" if get_scraper(codigo) else "❌"
        
        print(f"{scraper_disponible} {config['nombre']}")
        print(f"   Código: {codigo}")
        print(f"   Estado: {estado}")
        print(f"   Prioridad: {config['prioridad']}")
        print(f"   URL: {config['url_noticias']}")
        print()

__all__ = [
    'FUENTES_CONFIG',
    'get_fuentes_activas',
    'get_fuente_config',
    'get_fuentes_por_prioridad',
    'is_fuente_activa',
    'get_fuente_nombre',
    'get_fuente_url',
    'get_fuente_palabras_clave',
    'get_fuente_exclusiones',
    'SCRAPERS_DISPONIBLES',
    'get_scraper',
    'get_scrapers_activos',
    'listar_fuentes_disponibles',
    'PoderJudicialScraper',
    'MinisterioJusticiaScraper',
    'DPPScraper',
    'ContraloriaScraper',
    'TDPScraper',
    'CDEScraper',
    'TDLScraper',
    'PrimerTribunalAmbientalScraper',
    'TercerTribunalAmbientalScraper',
    'TribunalAmbientalScraper'
] 
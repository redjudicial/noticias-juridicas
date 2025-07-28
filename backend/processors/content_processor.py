#!/usr/bin/env python3
"""
Procesador de contenido para noticias jurídicas
Genera resúmenes ejecutivos y procesa metadata
"""

import os
import sys
import re
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass
import openai
from dotenv import load_dotenv

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

@dataclass
class NoticiaCompleta:
    """Estructura completa de una noticia jurídica"""
    # Información básica (requerida)
    titulo: str
    titulo_original: str
    cuerpo_completo: str
    fecha_publicacion: datetime
    fuente: str
    fuente_nombre_completo: str
    url_origen: str
    
    # Contenido opcional
    subtitulo: Optional[str] = None
    resumen_ejecutivo: Optional[str] = None
    extracto_fuente: Optional[str] = None
    fecha_actualizacion: Optional[datetime] = None
    url_imagen: Optional[str] = None
    
    # Clasificación
    categoria: Optional[str] = None
    subcategoria: Optional[str] = None
    etiquetas: List[str] = None
    palabras_clave: List[str] = None
    
    # Información legal
    tipo_documento: Optional[str] = None
    jurisdiccion: Optional[str] = None
    tribunal_organismo: Optional[str] = None
    numero_causa: Optional[str] = None
    rol_causa: Optional[str] = None
    
    # Metadatos adicionales
    autor: Optional[str] = None
    autor_cargo: Optional[str] = None
    ubicacion: Optional[str] = None
    region: Optional[str] = None
    
    def __post_init__(self):
        if self.etiquetas is None:
            self.etiquetas = []
        if self.palabras_clave is None:
            self.palabras_clave = []
    
    def generate_hash(self) -> str:
        """Generar hash único del contenido"""
        content = f"{self.titulo}{self.cuerpo_completo}{self.fecha_publicacion.isoformat()}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def to_dict(self) -> Dict:
        """Convertir a diccionario para Supabase"""
        return {
            'titulo': self.titulo,
            'titulo_original': self.titulo_original,
            'subtitulo': self.subtitulo,
            'resumen_ejecutivo': self.resumen_ejecutivo,
            'cuerpo_completo': self.cuerpo_completo,
            'extracto_fuente': self.extracto_fuente,
            'fecha_publicacion': self.fecha_publicacion.isoformat(),
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'fuente': self.fuente,
            'fuente_nombre_completo': self.fuente_nombre_completo,
            'url_origen': self.url_origen,
            'url_imagen': self.url_imagen,
            'categoria': self.categoria,
            'subcategoria': self.subcategoria,
            'etiquetas': self.etiquetas,
            'palabras_clave': self.palabras_clave,
            'tipo_documento': self.tipo_documento,
            'jurisdiccion': self.jurisdiccion,
            'tribunal_organismo': self.tribunal_organismo,
            'numero_causa': self.numero_causa,
            'rol_causa': self.rol_causa,
            'autor': self.autor,
            'autor_cargo': self.autor_cargo,
            'ubicacion': self.ubicacion,
            'region': self.region,
            'hash_contenido': self.generate_hash()
        }

class ContentProcessor:
    """Procesador de contenido para noticias jurídicas"""
    
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def generar_resumen_ejecutivo(self, titulo: str, contenido: str, fuente: str) -> Dict[str, str]:
        """
        Genera un resumen ejecutivo completo con IA
        
        Returns:
            Dict con 'titulo_resumen', 'subtitulo', 'resumen_contenido', 'puntos_clave'
        """
        try:
            # Limpiar título y contenido
            titulo_limpio = self._limpiar_titulo(titulo)
            contenido_limpio = self._limpiar_contenido(contenido)
            
            if not self.openai_api_key:
                return self._generar_resumen_manual(titulo_limpio, contenido_limpio, fuente)
            
            # Preparar prompt para IA
            prompt = self._crear_prompt_resumen(titulo_limpio, contenido_limpio, fuente)
            
            # Llamar a OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en derecho chileno. Tu tarea es crear resúmenes ejecutivos claros y precisos de noticias jurídicas."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            # Procesar respuesta
            respuesta_ia = response.choices[0].message.content
            
            # Parsear la respuesta estructurada
            return self._parsear_respuesta_ia(respuesta_ia, titulo_limpio, contenido_limpio, fuente)
            
        except Exception as e:
            print(f"❌ Error generando resumen con IA: {str(e)}")
            return self._generar_resumen_manual(titulo, contenido, fuente)
    
    def _crear_prompt_resumen(self, titulo: str, contenido: str, fuente: str) -> str:
        """Crear prompt estructurado para IA"""
        return f"""
        Título: {titulo}
        Fuente: {fuente}
        Contenido: {contenido[:2000]}...

        Genera un resumen ejecutivo directo y práctico con el siguiente formato:

        RESUMEN: [Un solo párrafo de máximo 200 palabras que explique directamente los hechos principales, sin frases introductorias como "esta noticia trata" o "se informa que". Ir directo al grano con los hechos más importantes]
        PALABRAS_CLAVE: [3 palabras clave separadas por comas, sin espacios extras]

        El resumen debe ser:
        - Directo y práctico (NO usar "esta noticia trata", "se informa que", etc.)
        - Un solo párrafo completo (no cortado)
        - Máximo 200 palabras
        - Ir inmediatamente a los hechos principales
        - Claro y comprensible para abogados
        - Incluir información jurídica relevante
        - Mantener precisión legal
        - NO cambiar el título original
        - Nada de relleno, solo información esencial

        Ejemplo de formato correcto:
        "El presidente Boric inauguró la nueva cárcel de Rancagua con capacidad para 1,200 internos. La infraestructura incluye áreas de trabajo, educación y rehabilitación. El proyecto tuvo una inversión de $45 mil millones y reducirá el hacinamiento carcelario en la región."

        Las palabras clave deben ser:
        - 3 términos jurídicos relevantes
        - Separadas por comas
        - Sin espacios extras
        """
    
    def _parsear_respuesta_ia(self, respuesta: str, titulo: str, contenido: str, fuente: str) -> Dict[str, str]:
        """Parsear respuesta estructurada de IA"""
        try:
            # Extraer secciones usando regex
            resumen_match = re.search(r'RESUMEN:\s*(.+?)(?=\nPALABRAS_CLAVE:|$)', respuesta, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            palabras_match = re.search(r'PALABRAS_CLAVE:\s*(.+)', respuesta, re.IGNORECASE | re.MULTILINE)
            
            # Procesar palabras clave
            palabras_clave = []
            if palabras_match:
                palabras_texto = palabras_match.group(1).strip()
                palabras_clave = [palabra.strip() for palabra in palabras_texto.split(',') if palabra.strip()]
                # Limitar a 3 palabras clave
                palabras_clave = palabras_clave[:3]
            
            # Generar resumen
            resumen_contenido = resumen_match.group(1).strip() if resumen_match else self._generar_resumen_basico(contenido)
            
            return {
                'titulo_resumen': titulo,  # Mantener título original
                'subtitulo': "",
                'resumen_contenido': resumen_contenido,
                'puntos_clave': [],
                'implicaciones_juridicas': "",
                'palabras_clave': palabras_clave,
                'fuente': fuente
            }
            
        except Exception as e:
            print(f"❌ Error parseando respuesta IA: {str(e)}")
            return self._generar_resumen_manual(titulo, contenido, fuente)
    
    def _generar_resumen_manual(self, titulo: str, contenido: str, fuente: str) -> Dict[str, str]:
        """Generar resumen manual cuando IA no está disponible"""
        # Limpiar título y contenido
        titulo_limpio = self._limpiar_titulo(titulo)
        contenido_limpio = self._limpiar_contenido(contenido)
        
        # Extraer información clave del contenido
        fecha = self._extraer_fecha(contenido)
        tribunal = self._extraer_tribunal(contenido)
        
        # Generar resumen básico directo
        resumen = titulo_limpio
        if tribunal:
            resumen += f" del {tribunal}"
        if fecha:
            resumen += f" con fecha {fecha}"
        resumen += ". "
        
        # Agregar información adicional del contenido si está disponible
        if len(contenido_limpio) > 50:
            # Tomar las primeras 100 palabras del contenido para complementar
            palabras_adicionales = contenido_limpio.split()[:100]
            contenido_adicional = ' '.join(palabras_adicionales)
            resumen += contenido_adicional.strip()
            if not resumen.endswith('.'):
                resumen += '.'
        
        return {
            'titulo_resumen': titulo_limpio,
            'subtitulo': "",
            'resumen_contenido': resumen,
            'puntos_clave': [],
            'implicaciones_juridicas': "",
            'palabras_clave': [],  # Eliminar palabras clave
            'fuente': fuente
        }
    
    def _generar_resumen_basico(self, contenido: str) -> str:
        """Generar resumen básico del contenido"""
        # Limpiar contenido de información irrelevante
        contenido_limpio = self._limpiar_contenido(contenido)
        
        # Tomar las primeras 150 palabras y limpiar
        palabras = contenido_limpio.split()[:150]
        resumen = ' '.join(palabras)
        
        # Limpiar y formatear
        resumen = re.sub(r'\s+', ' ', resumen)
        resumen = resumen.strip()
        
        # Asegurar que termine con punto
        if resumen and not resumen.endswith(('.', '!', '?')):
            resumen += '.'
        
        return resumen
    
    def _limpiar_contenido(self, contenido: str) -> str:
        """Limpiar contenido de información irrelevante"""
        # Patrones a eliminar
        patrones_a_eliminar = [
            r'Poder Judicial Radio.*?Compartir',
            r'Los horarios de atención son.*?horas\.',
            r'Atención por teléfonos.*?\d+',
            r'Licitaciones del Poder Judicial.*?Licitaciones adjudicadas',
            r'Prensa y Comunicaciones.*?Proyectos de Ley',
            r'Consulta Ciudadana.*?Sistema de traducción',
            r'Canal preferencial.*?creole\.',
            r'\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}',  # Fechas con hora
            r'\d{2}:\d{2}',  # Horas sueltas
            r'Compartir\s+Compartir',
            r'Compartir\s*',  # Solo "Compartir"
            r'×\s*',  # Símbolos de multiplicación
            r'Portal Unificado de Sentencias.*?Compartir',
            r'Fiscalía.*?Compartir',
            r'Corte de Apelaciones.*?Compartir',
            r'Corte Suprema.*?Compartir',
            r'TOP.*?Compartir',
            r'Juzgado.*?Compartir',
        ]
        
        contenido_limpio = contenido
        
        # Aplicar cada patrón de limpieza
        for patron in patrones_a_eliminar:
            contenido_limpio = re.sub(patron, '', contenido_limpio, flags=re.IGNORECASE | re.DOTALL)
        
        # Limpiar espacios múltiples y líneas vacías
        contenido_limpio = re.sub(r'\s+', ' ', contenido_limpio)
        contenido_limpio = re.sub(r'\n\s*\n', '\n', contenido_limpio)
        
        return contenido_limpio.strip()
    
    def _limpiar_titulo(self, titulo: str) -> str:
        """Limpiar título de fechas y horas"""
        # Eliminar fechas y horas del título
        titulo_limpio = re.sub(r'\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}', '', titulo)
        titulo_limpio = re.sub(r'\d{2}:\d{2}', '', titulo_limpio)
        titulo_limpio = re.sub(r'\d{2}-\d{2}-\d{4}', '', titulo_limpio)  # Solo fecha
        titulo_limpio = re.sub(r'\s+', ' ', titulo_limpio).strip()
        
        return titulo_limpio
    
    def _extraer_puntos_clave(self, texto_puntos: str) -> List[str]:
        """Extraer puntos clave del texto"""
        puntos = []
        if texto_puntos:
            # Buscar líneas que empiecen con -
            lineas = texto_puntos.split('\n')
            for linea in lineas:
                linea = linea.strip()
                if linea.startswith('-') or linea.startswith('•'):
                    punto = linea[1:].strip()
                    if punto:
                        puntos.append(punto)
        
        # Si no hay puntos, generar algunos básicos
        if not puntos:
            puntos = [
                "Información jurídica relevante",
                "Actualización importante",
                "Recomendación de revisión"
            ]
        
        return puntos[:5]  # Máximo 5 puntos
    
    def _extraer_palabras_clave(self, texto: str) -> List[str]:
        """Extraer palabras clave del texto"""
        palabras_clave = [
            'sentencia', 'resolución', 'acuerdo', 'dictamen', 'informe',
            'audiencia', 'causa', 'rol', 'tribunal', 'corte', 'juzgado',
            'fiscalía', 'defensoría', 'contraloría', 'ministerio',
            'ley', 'decreto', 'reglamento', 'circular', 'instructivo',
            'penal', 'civil', 'laboral', 'ambiental', 'constitucional',
            'comercial', 'tributario', 'administrativo'
        ]
        
        encontradas = []
        texto_lower = texto.lower()
        
        for palabra in palabras_clave:
            if palabra in texto_lower:
                encontradas.append(palabra)
        
        return encontradas[:10]  # Máximo 10 palabras clave
    
    def _extraer_fecha(self, texto: str) -> Optional[str]:
        """Extraer fecha del texto"""
        patrones_fecha = [
            r'\d{2}/\d{2}/\d{4}',
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}-\d{2}-\d{4}'
        ]
        
        for patron in patrones_fecha:
            match = re.search(patron, texto)
            if match:
                return match.group()
        
        return None
    
    def _extraer_tribunal(self, texto: str) -> Optional[str]:
        """Extraer tribunal del texto"""
        tribunales = [
            'Corte Suprema', 'Corte de Apelaciones', 'Juzgado Civil', 'Juzgado Penal',
            'Tribunal Ambiental', 'Tribunal de Defensa de la Libre Competencia',
            'Contraloría', 'Fiscalía', 'Defensoría', 'Ministerio de Justicia'
        ]
        
        texto_lower = texto.lower()
        for tribunal in tribunales:
            if tribunal.lower() in texto_lower:
                return tribunal
        
        return None
    
    def procesar_noticia_completa(self, noticia_raw: Dict) -> Dict[str, any]:
        """Procesar noticia completa con resumen ejecutivo"""
        titulo = noticia_raw.get('titulo', '')
        contenido = noticia_raw.get('contenido', '')
        fuente = noticia_raw.get('fuente', '')
        
        # Generar resumen ejecutivo
        resumen = self.generar_resumen_ejecutivo(titulo, contenido, fuente)
        
        # Extraer metadata adicional
        metadata = self._extraer_metadata_completa(noticia_raw)
        
        return {
            'resumen_ejecutivo': resumen['resumen_contenido'],
            'titulo_resumen': resumen['titulo_resumen'],
            'subtitulo_resumen': resumen['subtitulo'],
            'puntos_clave': resumen['puntos_clave'],
            'implicaciones_juridicas': resumen['implicaciones_juridicas'],
            'metadata': metadata
        }
    
    def _extraer_metadata_completa(self, noticia_raw: Dict) -> Dict[str, any]:
        """Extraer metadata completa de la noticia"""
        contenido = noticia_raw.get('contenido', '')
        titulo = noticia_raw.get('titulo', '')
        url = noticia_raw.get('url', '')
        
        metadata = {
            'numero_palabras': len(contenido.split()),
            'idioma': 'es',
            'fecha_extraccion': datetime.now(timezone.utc).isoformat(),
            'url_original': url,
            'scraper_version': '2.0'
        }
        
        # Extraer información de causa
        rol_match = re.search(r'Rol\s+([A-Z]?\s*\d+-\d+)', contenido, re.IGNORECASE)
        if rol_match:
            metadata['rol_causa'] = rol_match.group(1).strip()
        
        # Extraer tribunal
        tribunal = self._extraer_tribunal(contenido)
        if tribunal:
            metadata['tribunal_organismo'] = tribunal
        
        # Extraer región
        regiones = [
            'Arica y Parinacota', 'Tarapacá', 'Antofagasta', 'Atacama', 'Coquimbo',
            'Valparaíso', 'Metropolitana', 'O\'Higgins', 'Maule', 'Ñuble',
            'Biobío', 'La Araucanía', 'Los Ríos', 'Los Lagos', 'Aysén', 'Magallanes'
        ]
        
        for region in regiones:
            if region.lower() in contenido.lower():
                metadata['region'] = region
                break
        
        # Extraer fecha
        fecha = self._extraer_fecha(contenido)
        if fecha:
            metadata['fecha_evento'] = fecha
        
        # Determinar relevancia
        palabras_importantes = ['sentencia', 'resolución', 'acuerdo', 'dictamen', 'audiencia']
        relevancia = 0
        for palabra in palabras_importantes:
            if palabra in contenido.lower():
                relevancia += 1
        
        metadata['relevancia_juridica'] = min(relevancia, 5)
        metadata['impacto_publico'] = min(relevancia, 3)
        
        return metadata 
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
        self.openai_api_key = openai_api_key
        self.resumen_cache = {}  # Cache para evitar llamadas repetidas or os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def generar_resumen_ejecutivo(self, titulo: str, contenido: str, fuente: str) -> Dict[str, str]:
        """
        Genera un resumen ejecutivo usando solo el primer párrafo (200 caracteres)
        
        Returns:
            Dict con 'titulo_resumen', 'subtitulo', 'resumen_contenido', 'puntos_clave'
        """
        try:
            # Limpiar título y contenido
            titulo_limpio = self._limpiar_titulo(titulo)
            contenido_limpio = self._limpiar_contenido(contenido)
            
            # Verificar cache
            cache_key = f"{titulo_limpio[:100]}_{fuente}"
            if cache_key in self.resumen_cache:
                return self.resumen_cache[cache_key]
            
            # Siempre usar resumen manual (sin IA)
            resultado = self._generar_resumen_manual(titulo_limpio, contenido_limpio, fuente)
            
            # Guardar en cache
            self.resumen_cache[cache_key] = resultado
            
            return resultado
            
        except Exception as e:
            print(f"❌ Error generando resumen: {str(e)}")
            return self._generar_resumen_manual(titulo, contenido, fuente)
    
    def _crear_prompt_resumen(self, titulo: str, contenido: str, fuente: str) -> str:
        """Crear prompt estructurado para IA"""
        return f"""
        Título: {titulo}
        Fuente: {fuente}
        Contenido: {contenido[:800]}...

        RESUMEN: [Máximo 80 palabras. Solo hechos principales]
        PALABRAS_CLAVE: [3 términos jurídicos separados por comas]

        REGLAS:
        - Máximo 80 palabras
        - Solo información esencial
        - Sin introducciones
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
        """Generar resumen manual usando solo el primer párrafo (400 caracteres) sin repetir título"""
        # Limpiar título y contenido
        titulo_limpio = self._limpiar_titulo(titulo)
        contenido_limpio = self._limpiar_contenido(contenido)
        
        # Extraer el primer párrafo
        primer_parrafo = self._extraer_primer_parrafo(contenido_limpio)
        
        # Eliminar repetición del título del contenido
        contenido_sin_titulo = self._eliminar_titulo_del_contenido(primer_parrafo, titulo_limpio)
        
        # Limitar a 400 caracteres y agregar (...)
        if len(contenido_sin_titulo) > 400:
            resumen = contenido_sin_titulo[:400].strip()
            # Asegurar que no corte en medio de una palabra
            if not resumen.endswith(' '):
                resumen = resumen.rsplit(' ', 1)[0]
            resumen += " (...)"
        else:
            resumen = contenido_sin_titulo
        
        return {
            'titulo_resumen': titulo_limpio,
            'subtitulo': "",
            'resumen_contenido': resumen,
            'puntos_clave': [],
            'implicaciones_juridicas': "",
            'palabras_clave': [],
            'fuente': fuente
        }
    
    def _eliminar_titulo_del_contenido(self, contenido: str, titulo: str) -> str:
        """Eliminar repetición del título del contenido"""
        if not contenido or not titulo:
            return contenido
        
        # Limpiar el título para comparación
        titulo_limpio = titulo.lower().strip()
        contenido_limpio = contenido.lower().strip()
        
        # Si el contenido empieza con el título, eliminarlo
        if contenido_limpio.startswith(titulo_limpio):
            # Encontrar donde termina el título en el contenido original
            titulo_original = titulo.strip()
            contenido_original = contenido.strip()
            
            # Buscar el título al inicio del contenido
            if contenido_original.lower().startswith(titulo_original.lower()):
                # Extraer el contenido después del título
                contenido_sin_titulo = contenido_original[len(titulo_original):].strip()
                
                # Limpiar caracteres extra al inicio (puntos, guiones, espacios)
                contenido_sin_titulo = re.sub(r'^[.\-\s]+', '', contenido_sin_titulo)
                
                return contenido_sin_titulo
        
        return contenido
    
    def _extraer_primer_parrafo(self, contenido: str) -> str:
        """Extraer el primer párrafo del contenido"""
        if not contenido:
            return ""
        
        # Dividir por párrafos (doble salto de línea)
        parrafos = contenido.split('\n\n')
        
        # Tomar el primer párrafo no vacío
        for parrafo in parrafos:
            parrafo_limpio = parrafo.strip()
            if parrafo_limpio and len(parrafo_limpio) > 10:  # Al menos 10 caracteres
                return parrafo_limpio
        
        # Si no hay párrafos claros, tomar las primeras 200 palabras
        palabras = contenido.split()[:200]
        return ' '.join(palabras)
    
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
        if not contenido:
            return ""
        
        # Patrones a eliminar
        patrones_a_eliminar = [
            # Información del Tribunal Ambiental (texto problemático)
            r'Acceder al expediente de la causa[A-Z0-9\-]+.*?contacto@tribunalambiental\.cl\.',
            r'Acceder al expediente[A-Z0-9\-]+.*?contacto@tribunalambiental\.cl\.',
            r'Morandé 360, Piso 8, Santiago.*?contacto@tribunalambiental\.cl\.',
            r'Piso 8, Santiago\([0-9\s\+]+\)contacto@tribunalambiental\.cl\.',
            r'\([0-9\s\+]+\)contacto@tribunalambiental\.cl\.',
            r'contacto@tribunalambiental\.cl\.',
            r'R-[0-9\-]+ Morandé 360, Piso 8, Santiago',
            r'Piso 8, Santiago\([0-9\s\+]+\), Piso 8, Santiago',
            
            # Información del Poder Judicial
            r'Poder Judicial Radio.*?Compartir',
            r'Los horarios de atención son.*?horas\.',
            r'Atención por teléfonos.*?\d+',
            r'Licitaciones del Poder Judicial.*?Licitaciones adjudicadas',
            r'Prensa y Comunicaciones.*?Proyectos de Ley',
            r'Consulta Ciudadana.*?Sistema de traducción',
            r'Canal preferencial.*?creole\.',
            
            # Fechas y horas
            r'\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}',  # Fechas con hora
            r'\d{2}:\d{2}',  # Horas sueltas
            
            # Elementos de navegación
            r'Compartir\s+Compartir',
            r'Compartir\s*',  # Solo "Compartir"
            r'×\s*',  # Símbolos de multiplicación
            r'Volver\s*',  # "Volver"
            r'Cerrar\s*',  # "Cerrar"
            
            # Portales y sistemas
            r'Portal Unificado de Sentencias.*?Compartir',
            r'Fiscalía.*?Compartir',
            r'Corte de Apelaciones.*?Compartir',
            r'Corte Suprema.*?Compartir',
            r'TOP.*?Compartir',
            r'Juzgado.*?Compartir',
            
            # Información de contacto y navegación
            r'Please ensure Javascript is enabled for purposes of website accessibility',
            r'Sistema de traducción en línea.*?\d+',
            r'Atención por Chat Messenger',
            r'Portal Unificado de Sentencias en línea',
            r'Orientación e información digital',
            r'Plataformas digitales destinadas a orientar.*?usuarios',
            r'Canal preferencial para personas en situación de discapacidad',
            r'Traducción automática.*?creole',
            
            # Números de teléfono y contacto
            r'\d{6,}',  # Números largos (teléfonos)
            r'Teléfono.*?\d+',
            r'Contacto.*?\d+',
            
            # Enlaces y URLs
            r'https?://[^\s]+',
            r'www\.[^\s]+',
            
            # Información de navegación
            r'Tabla Primera Sala',
            r'Tabla Segunda Sala',
            r'Compendio Tercera Sala Corte Suprema',
            r'Muestra representativa de sentencias.*?alto volumen',
            r'Materias a consultar.*?licencias médicas',
            r'Buscador Unificado de Sentencias',
            r'Contiene una.*?sentencias',
            
            # Información administrativa
            r'Los horarios de atención.*?horas',
            r'Horario de atención.*?horas',
            r'Días hábiles.*?viernes',
            r'Lunes a viernes.*?horas',
        ]
        
        contenido_limpio = contenido
        
        # Aplicar cada patrón de limpieza
        for patron in patrones_a_eliminar:
            contenido_limpio = re.sub(patron, '', contenido_limpio, flags=re.IGNORECASE | re.DOTALL)
        
        # Limpiar espacios múltiples y líneas vacías
        contenido_limpio = re.sub(r'\s+', ' ', contenido_limpio)
        contenido_limpio = re.sub(r'\n\s*\n', '\n', contenido_limpio)
        
        # Eliminar líneas que solo contengan espacios o caracteres especiales
        lineas = contenido_limpio.split('\n')
        lineas_limpias = []
        for linea in lineas:
            linea_limpia = linea.strip()
            if linea_limpia and len(linea_limpia) > 3:  # Al menos 3 caracteres
                # Verificar que no sea solo caracteres especiales
                if re.search(r'[a-zA-ZáéíóúñÁÉÍÓÚÑ]', linea_limpia):
                    lineas_limpias.append(linea_limpia)
        
        contenido_limpio = '\n'.join(lineas_limpias)
        
        # Limpiar espacios al inicio y final
        contenido_limpio = contenido_limpio.strip()
        
        return contenido_limpio
    
    def _limpiar_titulo(self, titulo: str) -> str:
        """Limpiar título de fechas, horas y información duplicada"""
        if not titulo:
            return ""
        
        titulo_limpio = titulo
        
        # Eliminar fechas y horas del título (más agresivo)
        patrones_fecha_hora = [
            # Patrones específicos para el ejemplo dado (fechas pegadas al final)
            r'\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}$',  # 01-08-2025 04:08
            r'\d{1,2}-\d{1,2}-\d{4}\s+\d{1,2}:\d{2}$',  # 1-8-2025 4:08
            r'\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}\s*$',  # Con espacios al final
            r'\d{1,2}-\d{1,2}-\d{4}\s+\d{1,2}:\d{2}\s*$',  # Con espacios al final
            
            # Patrones generales de fecha y hora
            r'\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}',  # DD-MM-YYYY HH:MM
            r'\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}',  # DD/MM/YYYY HH:MM
            r'\d{2}:\d{2}',  # Solo hora
            r'\d{2}-\d{2}-\d{4}',  # Solo fecha DD-MM-YYYY
            r'\d{2}/\d{2}/\d{4}',  # Solo fecha DD/MM/YYYY
            r'\d{4}-\d{2}-\d{2}',  # Solo fecha YYYY-MM-DD
            r'\d{1,2}-\d{1,2}-\d{4}\s+\d{1,2}:\d{2}',  # D-M-YYYY H:MM
            r'\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}',  # D/M/YYYY H:MM
            r'\d{1,2}-\d{1,2}-\d{4}',  # D-M-YYYY
            r'\d{1,2}/\d{1,2}/\d{4}',  # D/M/YYYY
            
            # Patrones específicos del Poder Judicial
            r'\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}\s*$',  # Fecha y hora al final
            r'\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}\s*$',  # Fecha y hora al final
            r'\d{1,2}-\d{1,2}-\d{4}\s+\d{1,2}:\d{2}\s*$',  # Fecha y hora al final
            r'\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}\s*$',  # Fecha y hora al final
            
            # Patrones específicos para el ejemplo dado
            r'\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}$',  # 26-07-2025 04:07
            r'\d{2}-\d{2}-\d{4}\s+\d{1,2}:\d{2}$',  # 26-07-2025 4:07
            r'\d{1,2}-\d{1,2}-\d{4}\s+\d{2}:\d{2}$',  # 6-07-2025 04:07
            r'\d{1,2}-\d{1,2}-\d{4}\s+\d{1,2}:\d{2}$',  # 6-7-2025 4:07
        ]
        
        for patron in patrones_fecha_hora:
            titulo_limpio = re.sub(patron, '', titulo_limpio)
        
        # Eliminar información duplicada y irrelevante
        patrones_duplicados = [
            r'\s+del\s+Corte\s+de\s+Apelaciones\.?\s*$',  # "del Corte de Apelaciones" al final
            r'\s+del\s+Fiscalía\.?\s*$',  # "del Fiscalía" al final
            r'\s+del\s+Corte\s+Suprema\.?\s*$',  # "del Corte Suprema" al final
            r'\s+del\s+TOP\.?\s*$',  # "del TOP" al final
            r'\s+del\s+Juzgado\.?\s*$',  # "del Juzgado" al final
            r'\s+Video\s*$',  # "Video" al final
            r'\s+Compartir\s*$',  # "Compartir" al final
            r'\s+×\s*$',  # Símbolo de multiplicación al final
            r'\s+Portal\s+Unificado\s+de\s+Sentencias\s*$',  # "Portal Unificado de Sentencias" al final
            r'\s+Poder\s+Judicial\s+Radio\s*$',  # "Poder Judicial Radio" al final
            r'\s+Poder\s+Judicial\s+TV\s*$',  # "Poder Judicial TV" al final
            r'\s+Orientación\s+e\s+información\s+digital\s*$',  # "Orientación e información digital" al final
            r'\s+Plataformas\s+digitales\s*$',  # "Plataformas digitales" al final
            r'\s+Atención\s+por\s+Chat\s*$',  # "Atención por Chat" al final
            r'\s+Sistema\s+de\s+traducción\s*$',  # "Sistema de traducción" al final
            r'\s+\d{6,}\s*$',  # Números largos al final (teléfonos)
            r'\s+creole\.\s*$',  # "creole." al final
            r'\s+Volver\s*$',  # "Volver" al final
            r'\s+Please\s+ensure\s+Javascript\s+is\s+enabled\s*$',  # "Please ensure Javascript is enabled" al final
            r'\s+Cerrar\s*$',  # "Cerrar" al final
        ]
        
        for patron in patrones_duplicados:
            titulo_limpio = re.sub(patron, '', titulo_limpio, flags=re.IGNORECASE)
        
        # Eliminar repeticiones del mismo título
        # Si el título se repite más de una vez, tomar solo la primera parte
        palabras = titulo_limpio.split()
        if len(palabras) > 10:
            # Buscar patrones de repetición
            mitad = len(palabras) // 2
            primera_mitad = ' '.join(palabras[:mitad])
            segunda_mitad = ' '.join(palabras[mitad:])
            
            # Si la segunda mitad es muy similar a la primera, eliminar la repetición
            if self._similitud_texto(primera_mitad, segunda_mitad) > 0.7:
                titulo_limpio = primera_mitad
        
        # Limpiar espacios múltiples y líneas vacías
        titulo_limpio = re.sub(r'\s+', ' ', titulo_limpio)
        titulo_limpio = titulo_limpio.strip()
        
        # Asegurar que no termine con punto si es muy corto
        if len(titulo_limpio) < 100 and titulo_limpio.endswith('.'):
            titulo_limpio = titulo_limpio[:-1]
        
        return titulo_limpio
    
    def _similitud_texto(self, texto1: str, texto2: str) -> float:
        """Calcular similitud entre dos textos (0-1)"""
        if not texto1 or not texto2:
            return 0.0
        
        # Convertir a minúsculas y dividir en palabras
        palabras1 = set(texto1.lower().split())
        palabras2 = set(texto2.lower().split())
        
        if not palabras1 or not palabras2:
            return 0.0
        
        # Calcular intersección
        interseccion = palabras1.intersection(palabras2)
        union = palabras1.union(palabras2)
        
        return len(interseccion) / len(union) if union else 0.0
    
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
    
    def _limpiar_duplicacion_titulo(self, titulo: str, contenido: str) -> str:
        """Eliminar el título del inicio del contenido si está duplicado"""
        # Limpiar el título de prefijos para comparar
        titulo_limpio = titulo
        if titulo.startswith('(') and ')' in titulo:
            titulo_limpio = titulo.split(')', 1)[1].strip()
        
        # Si el contenido comienza con el título (con o sin prefijo), quitarlo
        if contenido.startswith(titulo):
            contenido_limpio = contenido[len(titulo):].strip()
        elif contenido.startswith(titulo_limpio):
            contenido_limpio = contenido[len(titulo_limpio):].strip()
        else:
            # Buscar el título al inicio del contenido (más flexible)
            palabras_titulo = titulo_limpio.split()[:5]  # Primeras 5 palabras del título
            if len(palabras_titulo) >= 3:
                inicio_titulo = ' '.join(palabras_titulo[:3])
                if contenido.lower().startswith(inicio_titulo.lower()):
                    # Encontrar donde termina el título en el contenido
                    try:
                        fin_titulo = contenido.lower().find(inicio_titulo.lower()) + len(inicio_titulo)
                        # Buscar un punto de corte natural (fecha, punto, etc.)
                        resto = contenido[fin_titulo:]
                        if resto:
                            # Buscar el primer punto de corte natural
                            cortes = [' 20', '. ', '\n', '  ']
                            for corte in cortes:
                                idx = resto.find(corte)
                                if idx >= 0 and idx < 100:  # Dentro de los primeros 100 caracteres
                                    contenido_limpio = resto[idx:].strip()
                                    if corte.strip():
                                        contenido_limpio = contenido_limpio[len(corte):].strip()
                                    break
                            else:
                                contenido_limpio = contenido
                        else:
                            contenido_limpio = contenido
                    except:
                        contenido_limpio = contenido
                else:
                    contenido_limpio = contenido
            else:
                contenido_limpio = contenido
        
        # Eliminar fechas sueltas al inicio (formato DD mes YYYY o similar)
        import re
        contenido_limpio = re.sub(r'^\d{1,2}\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+\d{4}\s*', '', contenido_limpio, flags=re.IGNORECASE)
        
        return contenido_limpio.strip()

    def _aplicar_prefijo_fuente(self, titulo: str, contenido: str, fuente: str) -> Tuple[str, str]:
        """Aplicar prefijo según la fuente para tribunales ambientales"""
        # Primero limpiar duplicación del título
        contenido_limpio = self._limpiar_duplicacion_titulo(titulo, contenido)
        
        prefijos = {
            '1ta': '(1º)',
            '3ta': '(3º)',
            'tribunal_ambiental': '(2º)'
        }
        
        prefijo = prefijos.get(fuente)
        if prefijo:
            # Aplicar prefijo al título
            titulo_con_prefijo = f"{prefijo} {titulo}"
            
            # Aplicar prefijo al contenido limpio si no empieza con el prefijo
            if not contenido_limpio.startswith(prefijo):
                contenido_con_prefijo = f"{prefijo} {contenido_limpio}"
            else:
                contenido_con_prefijo = contenido_limpio
                
            return titulo_con_prefijo, contenido_con_prefijo
        
        return titulo, contenido_limpio
    
    def procesar_noticia_completa(self, noticia_raw: Dict) -> Dict[str, any]:
        """Procesar noticia completa con resumen ejecutivo"""
        titulo = noticia_raw.get('titulo', '')
        contenido = noticia_raw.get('contenido', '')
        fuente = noticia_raw.get('fuente', '')
        
        # Aplicar prefijos para tribunales ambientales
        titulo, contenido = self._aplicar_prefijo_fuente(titulo, contenido, fuente)
        
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
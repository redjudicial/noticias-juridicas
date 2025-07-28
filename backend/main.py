#!/usr/bin/env python3
"""
Sistema principal de noticias jurídicas
Ejecuta scraping, procesamiento y almacenamiento en Supabase
"""

import os
import sys
import time
import schedule
from datetime import datetime, timezone
from typing import List, Dict
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.database.supabase_client import SupabaseClient
from backend.processors.content_processor import ContentProcessor

# Importar scrapers desde la estructura modular
from backend.scrapers.fuentes import (
    PoderJudicialScraper,
    ContraloriaScraper,
    CDEScraper,
    TDLScraper,
    PrimerTribunalAmbientalScraper,
    TercerTribunalAmbientalScraper,
    TribunalAmbientalScraper,
    SIIScraper,
    TTAScraper,
    INAPIScraper,
    DTScraper
)

class NoticiasJuridicasSystem:
    """Sistema principal de noticias jurídicas"""
    
    def __init__(self):
        # Cargar configuración
        self.config = self._load_config()
        
        # Inicializar clientes
        self.supabase = SupabaseClient(
            url=self.config['supabase_url'],
            key=self.config['supabase_service_key']
        )
        
        self.content_processor = ContentProcessor(
            openai_api_key=self.config.get('openai_api_key')
        )
        
        # Inicializar scrapers (solo los que funcionan)
        self.scrapers = {
            'poder_judicial': PoderJudicialScraper(
                openai_api_key=self.config.get('openai_api_key')
            ),
            'contraloria': ContraloriaScraper(
                openai_api_key=self.config.get('openai_api_key')
            ),
            'cde': CDEScraper(
                openai_api_key=self.config.get('openai_api_key')
            ),
            'tdlc': TDLScraper(
                openai_api_key=self.config.get('openai_api_key')
            ),
            '1ta': PrimerTribunalAmbientalScraper(
                openai_api_key=self.config.get('openai_api_key')
            ),
            '3ta': TercerTribunalAmbientalScraper(
                openai_api_key=self.config.get('openai_api_key')
            ),
            'tribunal_ambiental': TribunalAmbientalScraper(
                openai_api_key=self.config.get('openai_api_key')
            ),
            'sii': SIIScraper(
                openai_api_key=self.config.get('openai_api_key')
            ),
            'tta': TTAScraper(
                openai_api_key=self.config.get('openai_api_key')
            ),
            'inapi': INAPIScraper(
                openai_api_key=self.config.get('openai_api_key')
            ),
            'dt': DTScraper(
                openai_api_key=self.config.get('openai_api_key')
            )
        }
        
        print("🚀 Sistema de noticias jurídicas inicializado")
        print(f"📊 Scrapers disponibles: {len(self.scrapers)}")
    
    def _load_config(self) -> Dict:
        """Cargar configuración desde variables de entorno"""
        return {
            'supabase_url': os.getenv('SUPABASE_URL', 'https://qfomiierchksyfhxoukj.supabase.co'),
            'supabase_service_key': os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'max_noticias_por_fuente': int(os.getenv('MAX_NOTICIAS_POR_FUENTE', '20')),
            'intervalo_actualizacion': int(os.getenv('INTERVALO_ACTUALIZACION', '900')),  # 15 minutos
        }
    
    def run_scraping_completo(self):
        """Ejecutar scraping completo de todas las fuentes"""
        print(f"\n🔄 Iniciando scraping completo - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        total_noticias_nuevas = 0
        total_noticias_actualizadas = 0
        errores = []
        
        # Procesar cada fuente
        for fuente_nombre, scraper in self.scrapers.items():
            try:
                print(f"\n📰 Procesando fuente: {fuente_nombre}")
                
                # Obtener noticias de la fuente
                noticias = scraper.scrape_noticias_recientes(
                    max_noticias=self.config['max_noticias_por_fuente']
                )
                
                if not noticias:
                    print(f"⚠️  No se encontraron noticias en {fuente_nombre}")
                    continue
                
                # Procesar cada noticia
                for noticia in noticias:
                    try:
                        resultado = self._procesar_noticia(noticia)
                        
                        if resultado['tipo'] == 'nueva':
                            total_noticias_nuevas += 1
                        elif resultado['tipo'] == 'actualizada':
                            total_noticias_actualizadas += 1
                            
                    except Exception as e:
                        error_msg = f"Error procesando noticia de {fuente_nombre}: {e}"
                        print(f"❌ {error_msg}")
                        errores.append(error_msg)
                
                # Registrar log de la fuente
                self._registrar_log_fuente(fuente_nombre, len(noticias), len(errores))
                
            except Exception as e:
                error_msg = f"Error procesando fuente {fuente_nombre}: {e}"
                print(f"❌ {error_msg}")
                errores.append(error_msg)
        
        # Resumen final
        print(f"\n📊 Resumen del scraping:")
        print(f"   ✅ Noticias nuevas: {total_noticias_nuevas}")
        print(f"   🔄 Noticias actualizadas: {total_noticias_actualizadas}")
        print(f"   ❌ Errores: {len(errores)}")
        
        if errores:
            print(f"\n⚠️  Errores encontrados:")
            for error in errores[:5]:  # Mostrar solo los primeros 5
                print(f"   - {error}")
    
    def _procesar_noticia(self, noticia) -> Dict:
        """Procesar una noticia individual"""
        # Verificar duplicados por URL (más confiable que hash)
        noticia_existente = self.supabase.get_noticia_by_url(noticia.url_origen)
        
        if noticia_existente:
            # Verificar si necesita actualización
            if self._necesita_actualizacion(noticia_existente, noticia):
                return self._actualizar_noticia(noticia_existente['id'], noticia)
            else:
                return {'tipo': 'duplicada', 'id': noticia_existente['id']}
        else:
            # Nueva noticia
            return self._insertar_noticia(noticia)
    
    def _necesita_actualizacion(self, noticia_existente: Dict, noticia_nueva) -> bool:
        """Verificar si una noticia necesita actualización"""
        # Comparar fechas de actualización
        fecha_actualizacion = noticia_existente.get('fecha_actualizacion')
        if fecha_actualizacion:
            fecha_existente = datetime.fromisoformat(fecha_actualizacion.replace('Z', '+00:00'))
        else:
            fecha_existente = datetime.fromisoformat(noticia_existente['fecha_publicacion'].replace('Z', '+00:00'))
        fecha_nueva = noticia_nueva.fecha_actualizacion or noticia_nueva.fecha_publicacion
        
        return fecha_nueva > fecha_existente
    
    def _insertar_noticia(self, noticia) -> Dict:
        """Insertar nueva noticia en Supabase"""
        try:
            # Generar resumen ejecutivo
            resumen = self.content_processor.generar_resumen_ejecutivo(noticia.titulo, noticia.cuerpo_completo, noticia.fuente)
            
            # Preparar datos para inserción
            if hasattr(noticia, 'to_dict'):
                datos_noticia = noticia.to_dict()
            else:
                # Si ya es un diccionario, usarlo directamente
                datos_noticia = noticia
            
            # Agregar resumen ejecutivo y palabras clave
            datos_noticia['resumen_ejecutivo'] = resumen.get('resumen_contenido', '')
            datos_noticia['palabras_clave'] = resumen.get('palabras_clave', [])
            
            # Asegurar que los campos requeridos estén presentes
            if 'autor' not in datos_noticia or datos_noticia['autor'] is None:
                datos_noticia['autor'] = None
            
            # Insertar noticia
            noticia_id = self.supabase.insert_noticia(datos_noticia)
            
            if noticia_id:
                print(f"✅ Nueva noticia insertada: {noticia.titulo[:50]}...")
                return {'tipo': 'nueva', 'id': noticia_id}
            
        except Exception as e:
            print(f"❌ Error insertando noticia: {e}")
            raise
    
    def _actualizar_noticia(self, noticia_id: str, noticia) -> Dict:
        """Actualizar noticia existente"""
        try:
            # Generar nuevo resumen
            resumen = self.content_processor.generar_resumen_ejecutivo(noticia.titulo, noticia.cuerpo_completo, noticia.fuente)
            
            # Actualizar datos
            datos_actualizacion = noticia.to_dict()
            datos_actualizacion['resumen_ejecutivo'] = resumen.get('resumen_contenido', '')
            datos_actualizacion['palabras_clave'] = resumen.get('palabras_clave', [])
            datos_actualizacion['es_actualizacion'] = True
            datos_actualizacion['version'] = 2  # Incrementar versión
            
            self.supabase.update_noticia(noticia_id, datos_actualizacion)
            
            # Actualizar resumen
            datos_resumen = {
                'noticia_id': noticia_id,
                'titulo_resumen': resumen.get('titulo_resumen', ''),
                'subtitulo_resumen': resumen.get('subtitulo', ''),
                'resumen_contenido': resumen.get('resumen_contenido', ''),
                'puntos_clave': resumen.get('puntos_clave', []),
                'implicaciones_juridicas': resumen.get('implicaciones_juridicas', ''),
                'tipo_resumen': 'ejecutivo',
                'nivel_tecnico': 'intermedio',
                'modelo_ia': 'gpt-4',
                'version': 2
            }
            
            self.supabase.insert_resumen(datos_resumen)
            
            print(f"🔄 Noticia actualizada: {noticia.titulo[:50]}...")
            return {'tipo': 'actualizada', 'id': noticia_id}
            
        except Exception as e:
            print(f"❌ Error actualizando noticia: {e}")
            raise
    
    def _registrar_log_fuente(self, fuente: str, noticias_procesadas: int, errores: int):
        """Registrar log de procesamiento de fuente"""
        try:
            log_data = {
                'fuente_nombre': fuente,
                'estado': 'completado' if errores == 0 else 'error',
                'tipo_operacion': 'scraping',
                'noticias_encontradas': noticias_procesadas,
                'noticias_nuevas': noticias_procesadas,  # Simplificado
                'errores': errores,
                'duracion_segundos': 0,  # Se podría calcular
                'requests_realizados': noticias_procesadas
            }
            
            self.supabase.insert_log(log_data)
            
        except Exception as e:
            print(f"⚠️  Error registrando log: {e}")
    
    def run_once(self):
        """Ejecutar una vez"""
        print("🎯 Ejecutando scraping una vez...")
        self.run_scraping_completo()
    
    def run_scheduled(self):
        """Ejecutar en modo programado"""
        print(f"⏰ Iniciando modo programado - Intervalo: {self.config['intervalo_actualizacion']} segundos")
        
        # Programar ejecución
        schedule.every(self.config['intervalo_actualizacion']).seconds.do(self.run_scraping_completo)
        
        # Ejecutar inmediatamente la primera vez
        self.run_scraping_completo()
        
        # Mantener ejecutando
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
            except KeyboardInterrupt:
                print("\n🛑 Deteniendo sistema...")
                break
            except Exception as e:
                print(f"❌ Error en ejecución programada: {e}")
                time.sleep(300)  # Esperar 5 minutos antes de reintentar
    
    def get_estadisticas(self) -> Dict:
        """Obtener estadísticas del sistema"""
        try:
            stats = {
                'total_noticias': self.supabase.count_noticias(),
                'noticias_hoy': self.supabase.count_noticias_hoy(),
                'fuentes_activas': len(self.scrapers),
                'ultima_actualizacion': self.supabase.get_ultima_actualizacion(),
                'resumenes_generados': self.supabase.count_resumenes()
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return {}

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema de noticias jurídicas')
    parser.add_argument('--once', action='store_true', help='Ejecutar una sola vez')
    parser.add_argument('--scheduled', action='store_true', help='Ejecutar en modo programado')
    parser.add_argument('--stats', action='store_true', help='Mostrar estadísticas')
    parser.add_argument('--test-mode', action='store_true', help='Ejecutar en modo prueba')
    parser.add_argument('--working-only', action='store_true', help='Solo fuentes que funcionan')
    parser.add_argument('--max-noticias', type=int, default=20, help='Máximo número de noticias por fuente')
    parser.add_argument('--quick', action='store_true', help='Ejecución rápida')
    
    args = parser.parse_args()
    
    try:
        system = NoticiasJuridicasSystem()
        
        if args.stats:
            stats = system.get_estadisticas()
            print("\n📊 Estadísticas del sistema:")
            for key, value in stats.items():
                print(f"   {key}: {value}")
        
        elif args.once:
            print(f"🎯 Ejecutando scraping una vez (max: {args.max_noticias} noticias por fuente)")
            system.run_once()
        
        elif args.scheduled:
            system.run_scheduled()
        
        else:
            # Modo por defecto: ejecutar una vez
            system.run_once()
    
    except Exception as e:
        print(f"❌ Error en el sistema: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 
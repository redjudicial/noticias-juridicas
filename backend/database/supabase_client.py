#!/usr/bin/env python3
"""
Cliente de Supabase para noticias jurídicas
Maneja todas las operaciones de base de datos
"""

import os
import requests
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import time

class SupabaseClient:
    """Cliente para interactuar con Supabase"""
    
    def __init__(self, url: str, key: str):
        self.url = url.rstrip('/')
        self.key = key
        self.headers = {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
    
    def test_connection(self) -> bool:
        """Probar conexión a Supabase"""
        try:
            response = requests.get(f'{self.url}/rest/v1/', headers=self.headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    # ========================================
    # OPERACIONES DE NOTICIAS
    # ========================================
    
    def insert_noticia(self, datos: Any) -> Optional[str]:
        """Insertar nueva noticia"""
        try:
            # Convertir NoticiaEstandarizada a dict si es necesario
            if hasattr(datos, '__dict__'):
                # Es un objeto, convertir a dict
                datos_dict = {
                    'titulo': datos.titulo,
                    'cuerpo_completo': datos.cuerpo_completo,
                    'url_origen': datos.url_origen,
                    'fecha_publicacion': datos.fecha_publicacion.isoformat() if datos.fecha_publicacion else None,
                    'fuente': datos.fuente,
                    'categoria': datos.categoria.value if hasattr(datos.categoria, 'value') else str(datos.categoria),
                    'jurisdiccion': datos.jurisdiccion.value if hasattr(datos.jurisdiccion, 'value') else str(datos.jurisdiccion),
                    'tipo_documento': datos.tipo_documento.value if hasattr(datos.tipo_documento, 'value') else str(datos.tipo_documento),
                    'palabras_clave': datos.palabras_clave,
                    'hash_contenido': datos.hash_contenido if hasattr(datos, 'hash_contenido') else None
                }
            else:
                # Ya es un dict
                datos_dict = datos
            
            response = requests.post(
                f'{self.url}/rest/v1/noticias_juridicas',
                headers=self.headers,
                json=datos_dict
            )
            
            if response.status_code == 201:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0]['id']
                elif isinstance(result, dict):
                    return result.get('id')
            
            print(f"❌ Error insertando noticia: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            print(f"❌ Error en insert_noticia: {e}")
            return None
    
    def update_noticia(self, noticia_id: str, datos: Dict) -> bool:
        """Actualizar noticia existente"""
        try:
            response = requests.patch(
                f'{self.url}/rest/v1/noticias_juridicas?id=eq.{noticia_id}',
                headers=self.headers,
                json=datos
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Error en update_noticia: {e}")
            return False
    
    def get_noticia_by_hash(self, hash_contenido: str) -> Optional[Dict]:
        """Obtener noticia por hash de contenido"""
        try:
            response = requests.get(
                f'{self.url}/rest/v1/noticias_juridicas?hash_contenido=eq.{hash_contenido}&limit=1',
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0]
            
            return None
            
        except Exception as e:
            print(f"❌ Error en get_noticia_by_hash: {e}")
            return None
    
    def get_noticia_by_url(self, url_origen: str) -> Optional[Dict]:
        """Obtener noticia por URL (más confiable para evitar duplicados)"""
        try:
            response = requests.get(
                f'{self.url}/rest/v1/noticias_juridicas?url_origen=eq.{url_origen}&limit=1',
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0]
            
            return None
            
        except Exception as e:
            print(f"❌ Error en get_noticia_by_url: {e}")
            return None
    
    def get_noticias_recientes(self, limit: int = 10, offset: int = 0, fuente: str = None) -> List[Dict]:
        """Obtener noticias recientes"""
        try:
            url = f'{self.url}/rest/v1/noticias_juridicas?order=fecha_publicacion.desc&limit={limit}&offset={offset}'
            
            if fuente:
                url += f'&fuente=eq.{fuente}'
            
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            
            return []
            
        except Exception as e:
            print(f"❌ Error en get_noticias_recientes: {e}")
            return []
    
    def count_noticias(self) -> int:
        """Contar total de noticias"""
        try:
            response = requests.get(
                f'{self.url}/rest/v1/noticias_juridicas?select=count',
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0]['count']
            
            return 0
            
        except Exception as e:
            print(f"❌ Error en count_noticias: {e}")
            return 0
    
    def count_noticias_hoy(self) -> int:
        """Contar noticias de hoy"""
        try:
            hoy = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            response = requests.get(
                f'{self.url}/rest/v1/noticias_juridicas?fecha_publicacion=gte.{hoy}&select=count',
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0]['count']
            
            return 0
            
        except Exception as e:
            print(f"❌ Error en count_noticias_hoy: {e}")
            return 0
    
    # ========================================
    # OPERACIONES DE RESÚMENES
    # ========================================
    
    def insert_resumen(self, datos: Dict) -> Optional[str]:
        """Insertar nuevo resumen"""
        try:
            response = requests.post(
                f'{self.url}/rest/v1/noticias_resumenes_juridicos',
                headers=self.headers,
                json=datos
            )
            
            if response.status_code == 201:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0]['id']
                elif isinstance(result, dict):
                    return result.get('id')
            
            print(f"❌ Error insertando resumen: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            print(f"❌ Error en insert_resumen: {e}")
            return None
    
    def get_resumenes_noticia(self, noticia_id: str) -> List[Dict]:
        """Obtener resúmenes de una noticia"""
        try:
            response = requests.get(
                f'{self.url}/rest/v1/noticias_resumenes_juridicos?noticia_id=eq.{noticia_id}&order=fecha_generacion.desc',
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            
            return []
            
        except Exception as e:
            print(f"❌ Error en get_resumenes_noticia: {e}")
            return []
    
    def count_resumenes(self) -> int:
        """Contar total de resúmenes"""
        try:
            response = requests.get(
                f'{self.url}/rest/v1/noticias_resumenes_juridicos?select=count',
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0]['count']
            
            return 0
            
        except Exception as e:
            print(f"❌ Error en count_resumenes: {e}")
            return 0
    
    # ========================================
    # OPERACIONES DE LOGS
    # ========================================
    
    def insert_log(self, datos: Dict) -> Optional[str]:
        """Insertar log de scraping"""
        try:
            response = requests.post(
                f'{self.url}/rest/v1/noticias_logs_scraping',
                headers=self.headers,
                json=datos
            )
            
            if response.status_code == 201:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0]['id']
                elif isinstance(result, dict):
                    return result.get('id')
            
            return None
            
        except Exception as e:
            print(f"❌ Error en insert_log: {e}")
            return None
    
    def get_logs_recientes(self, limit: int = 50) -> List[Dict]:
        """Obtener logs recientes"""
        try:
            response = requests.get(
                f'{self.url}/rest/v1/noticias_logs_scraping?order=created_at.desc&limit={limit}',
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            
            return []
            
        except Exception as e:
            print(f"❌ Error en get_logs_recientes: {e}")
            return []
    
    # ========================================
    # OPERACIONES DE FUENTES
    # ========================================
    
    def get_fuentes_activas(self) -> List[Dict]:
        """Obtener fuentes activas"""
        try:
            response = requests.get(
                f'{self.url}/rest/v1/noticias_fuentes?activa=eq.true',
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            
            return []
            
        except Exception as e:
            print(f"❌ Error en get_fuentes_activas: {e}")
            return []
    
    def update_fuente_ultima_actualizacion(self, fuente_id: int) -> bool:
        """Actualizar última actualización de una fuente"""
        try:
            datos = {
                'ultima_actualizacion': datetime.now(timezone.utc).isoformat(),
                'proxima_actualizacion': None  # Se calculará automáticamente
            }
            
            response = requests.patch(
                f'{self.url}/rest/v1/noticias_fuentes?id=eq.{fuente_id}',
                headers=self.headers,
                json=datos
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Error en update_fuente_ultima_actualizacion: {e}")
            return False
    
    # ========================================
    # OPERACIONES DE ESTADÍSTICAS
    # ========================================
    
    def get_ultima_actualizacion(self) -> Optional[str]:
        """Obtener fecha de última actualización"""
        try:
            response = requests.get(
                f'{self.url}/rest/v1/noticias_juridicas?order=fecha_scraping.desc&limit=1&select=fecha_scraping',
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0]['fecha_scraping']
            
            return None
            
        except Exception as e:
            print(f"❌ Error en get_ultima_actualizacion: {e}")
            return None
    
    def get_estadisticas_fuentes(self) -> Dict[str, int]:
        """Obtener estadísticas por fuente"""
        try:
            response = requests.get(
                f'{self.url}/rest/v1/noticias_juridicas?select=fuente,count&group=fuente',
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                return {item['fuente']: item['count'] for item in result}
            
            return {}
            
        except Exception as e:
            print(f"❌ Error en get_estadisticas_fuentes: {e}")
            return {}
    
    def get_estadisticas_categorias(self) -> Dict[str, int]:
        """Obtener estadísticas por categoría"""
        try:
            response = requests.get(
                f'{self.url}/rest/v1/noticias_juridicas?select=categoria,count&group=categoria&categoria=not.is.null',
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                return {item['categoria']: item['count'] for item in result}
            
            return {}
            
        except Exception as e:
            print(f"❌ Error en get_estadisticas_categorias: {e}")
            return {}
    
    # ========================================
    # OPERACIONES DE BÚSQUEDA
    # ========================================
    
    def buscar_noticias(self, query: str, limit: int = 20, offset: int = 0) -> List[Dict]:
        """Buscar noticias por texto"""
        try:
            # Búsqueda en título y contenido
            url = f'{self.url}/rest/v1/noticias_juridicas?or=(titulo.ilike.%{query}%,cuerpo_completo.ilike.%{query}%,resumen_ejecutivo.ilike.%{query}%)&order=fecha_publicacion.desc&limit={limit}&offset={offset}'
            
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            
            return []
            
        except Exception as e:
            print(f"❌ Error en buscar_noticias: {e}")
            return []
    
    def buscar_por_fuente(self, fuente: str, limit: int = 20, offset: int = 0) -> List[Dict]:
        """Buscar noticias por fuente"""
        try:
            response = requests.get(
                f'{self.url}/rest/v1/noticias_juridicas?fuente=eq.{fuente}&order=fecha_publicacion.desc&limit={limit}&offset={offset}',
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            
            return []
            
        except Exception as e:
            print(f"❌ Error en buscar_por_fuente: {e}")
            return []
    
    def buscar_por_categoria(self, categoria: str, limit: int = 20, offset: int = 0) -> List[Dict]:
        """Buscar noticias por categoría"""
        try:
            response = requests.get(
                f'{self.url}/rest/v1/noticias_juridicas?categoria=eq.{categoria}&order=fecha_publicacion.desc&limit={limit}&offset={offset}',
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            
            return []
            
        except Exception as e:
            print(f"❌ Error en buscar_por_categoria: {e}")
            return []
    
    # ========================================
    # OPERACIONES DE LIMPIEZA
    # ========================================
    
    def limpiar_noticias_duplicadas(self) -> int:
        """Limpiar noticias duplicadas por hash"""
        try:
            # Obtener hashes duplicados
            response = requests.get(
                f'{self.url}/rest/v1/noticias_juridicas?select=hash_contenido,count&group=hash_contenido&count=gt.1',
                headers=self.headers
            )
            
            if response.status_code != 200:
                return 0
            
            hashes_duplicados = response.json()
            eliminadas = 0
            
            for item in hashes_duplicados:
                hash_contenido = item['hash_contenido']
                
                # Obtener todas las noticias con ese hash
                response = requests.get(
                    f'{self.url}/rest/v1/noticias_juridicas?hash_contenido=eq.{hash_contenido}&order=created_at.asc',
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    noticias = response.json()
                    
                    # Mantener la más antigua, eliminar las demás
                    for noticia in noticias[1:]:
                        delete_response = requests.delete(
                            f'{self.url}/rest/v1/noticias_juridicas?id=eq.{noticia["id"]}',
                            headers=self.headers
                        )
                        
                        if delete_response.status_code == 200:
                            eliminadas += 1
            
            return eliminadas
            
        except Exception as e:
            print(f"❌ Error en limpiar_noticias_duplicadas: {e}")
            return 0
    
    def limpiar_noticias_antiguas(self, dias: int = 30) -> int:
        """Limpiar noticias más antiguas que X días"""
        try:
            fecha_limite = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            fecha_limite = fecha_limite.replace(day=fecha_limite.day - dias)
            
            # Obtener noticias antiguas
            response = requests.get(
                f'{self.url}/rest/v1/noticias_juridicas?fecha_publicacion=lt.{fecha_limite.isoformat()}&select=id',
                headers=self.headers
            )
            
            if response.status_code != 200:
                return 0
            
            noticias_antiguas = response.json()
            eliminadas = 0
            
            for noticia in noticias_antiguas:
                delete_response = requests.delete(
                    f'{self.url}/rest/v1/noticias_juridicas?id=eq.{noticia["id"]}',
                    headers=self.headers
                )
                
                if delete_response.status_code == 200:
                    eliminadas += 1
            
            return eliminadas
            
        except Exception as e:
            print(f"❌ Error en limpiar_noticias_antiguas: {e}")
            return 0

# Función de prueba
def test_supabase_client():
    """Función de prueba del cliente Supabase"""
    # Cargar configuración
    supabase_url = os.getenv('SUPABASE_URL', 'https://qfomiierchksyfhxoukj.supabase.co')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_key:
        print("❌ Error: No se encontró SUPABASE_SERVICE_ROLE_KEY")
        return
    
    client = SupabaseClient(supabase_url, supabase_key)
    
    print("🧪 Probando cliente Supabase...")
    
    # Probar conexión
    if client.test_connection():
        print("✅ Conexión exitosa")
        
        # Probar estadísticas
        total_noticias = client.count_noticias()
        print(f"📊 Total noticias: {total_noticias}")
        
        # Probar obtener noticias recientes
        noticias = client.get_noticias_recientes(5)
        print(f"📰 Noticias recientes: {len(noticias)}")
        
        if noticias:
            print(f"   Última: {noticias[0]['titulo'][:50]}...")
        
        # Probar estadísticas por fuente
        stats_fuentes = client.get_estadisticas_fuentes()
        print(f"📈 Estadísticas por fuente: {stats_fuentes}")
        
    else:
        print("❌ Error de conexión")

if __name__ == "__main__":
    test_supabase_client() 
#!/usr/bin/env python3
"""
Integrar solución de manejo de duplicados en el scraper de Contraloría
"""

import os
import sys
import requests
import hashlib
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('../APIS_Y_CREDENCIALES.env')

# Configuración de Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://qfomiierchksyfhxoukj.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def verificar_noticia_existente(url):
    """Verificar si una noticia ya existe por URL"""
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}'
        }
        
        response = requests.get(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?select=*&url_origen=eq.{url}&limit=1',
            headers=headers
        )
        
        if response.status_code == 200:
            noticias = response.json()
            return noticias[0] if noticias else None
        else:
            print(f"❌ Error verificando noticia: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return None

def actualizar_noticia_existente(noticia_id, datos_nuevos):
    """Actualizar una noticia existente"""
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        
        response = requests.patch(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas?id=eq.{noticia_id}',
            headers=headers,
            json=datos_nuevos
        )
        
        if response.status_code == 204:
            print(f"✅ Noticia {noticia_id} actualizada correctamente")
            return True
        else:
            print(f"❌ Error actualizando noticia: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en actualización: {e}")
        return False

def insertar_noticia_nueva(datos):
    """Insertar una nueva noticia"""
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        
        response = requests.post(
            f'{SUPABASE_URL}/rest/v1/noticias_juridicas',
            headers=headers,
            json=datos
        )
        
        if response.status_code == 201:
            print("✅ Nueva noticia insertada correctamente")
            return True
        elif response.status_code == 409:
            print("⚠️ Noticia duplicada detectada (409)")
            return False
        else:
            print(f"❌ Error insertando noticia: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en inserción: {e}")
        return False

def generar_hash_contenido(titulo, contenido, url):
    """Generar hash único para el contenido"""
    contenido_para_hash = f"{titulo}|{contenido[:200]}|{url}"
    return hashlib.md5(contenido_para_hash.encode('utf-8')).hexdigest()

def crear_scraper_contraloria_mejorado():
    """Crear una versión mejorada del scraper de Contraloría con manejo de duplicados"""
    print("🔧 **CREANDO SCRAPER MEJORADO - CONTRALORÍA**")
    print("=" * 60)
    
    # Leer el scraper actual
    scraper_path = "../backend/scrapers/fuentes/contraloria/contraloria_scraper.py"
    
    if not os.path.exists(scraper_path):
        print("❌ Archivo del scraper no encontrado")
        return
    
    try:
        with open(scraper_path, 'r') as f:
            contenido_actual = f.read()
        
        print("✅ Archivo del scraper leído correctamente")
        
        # Agregar funciones de manejo de duplicados
        funciones_duplicados = '''

    def verificar_noticia_existente(self, url: str) -> Optional[Dict]:
        """Verificar si una noticia ya existe por URL"""
        try:
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}'
            }
            
            response = requests.get(
                f'{self.supabase_url}/rest/v1/noticias_juridicas?select=*&url_origen=eq.{url}&limit=1',
                headers=headers
            )
            
            if response.status_code == 200:
                noticias = response.json()
                return noticias[0] if noticias else None
            else:
                self._log_warning(f"Error verificando noticia: {response.status_code}")
                return None
                
        except Exception as e:
            self._log_warning(f"Error en verificación: {e}")
            return None

    def actualizar_noticia_existente(self, noticia_id: str, datos_nuevos: Dict) -> bool:
        """Actualizar una noticia existente"""
        try:
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal'
            }
            
            response = requests.patch(
                f'{self.supabase_url}/rest/v1/noticias_juridicas?id=eq.{noticia_id}',
                headers=headers,
                json=datos_nuevos
            )
            
            if response.status_code == 204:
                self._log_info(f"Noticia {noticia_id} actualizada correctamente")
                return True
            else:
                self._log_warning(f"Error actualizando noticia: {response.status_code}")
                return False
                
        except Exception as e:
            self._log_warning(f"Error en actualización: {e}")
            return False

    def insertar_noticia_nueva(self, datos: Dict) -> bool:
        """Insertar una nueva noticia con manejo de duplicados"""
        try:
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal'
            }
            
            response = requests.post(
                f'{self.supabase_url}/rest/v1/noticias_juridicas',
                headers=headers,
                json=datos
            )
            
            if response.status_code == 201:
                self._log_success("Nueva noticia insertada correctamente")
                return True
            elif response.status_code == 409:
                self._log_warning("Noticia duplicada detectada (409)")
                return False
            else:
                self._log_error(f"Error insertando noticia: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self._log_error(f"Error en inserción: {e}")
            return False

    def procesar_noticia_contraloria(self, noticia_data: Dict) -> bool:
        """Procesar una noticia de Contraloría con manejo de duplicados"""
        try:
            # Extraer datos de la noticia
            titulo = noticia_data.get('titulo', '')
            contenido = noticia_data.get('contenido', '')
            url = noticia_data.get('url_origen', '')
            fecha = noticia_data.get('fecha_publicacion', '')
            
            if not titulo or not url:
                self._log_warning("Datos incompletos de noticia")
                return False
            
            # Generar hash único
            hash_contenido = self.generar_hash_contenido(titulo, contenido, url)
            
            # Verificar si la noticia ya existe
            noticia_existente = self.verificar_noticia_existente(url)
            
            if noticia_existente:
                self._log_info(f"Noticia existente encontrada: {titulo[:50]}...")
                
                # Preparar datos para actualización
                datos_actualizacion = {
                    'titulo': titulo,
                    'contenido': contenido,
                    'hash_contenido': hash_contenido,
                    'fecha_actualizacion': datetime.now().isoformat()
                }
                
                # Actualizar noticia existente
                return self.actualizar_noticia_existente(noticia_existente['id'], datos_actualizacion)
            else:
                self._log_info(f"Nueva noticia: {titulo[:50]}...")
                
                # Preparar datos para inserción
                datos_insercion = {
                    'titulo': titulo,
                    'contenido': contenido,
                    'url_origen': url,
                    'fuente': 'contraloria',
                    'fecha_publicacion': fecha,
                    'hash_contenido': hash_contenido,
                    'fecha_actualizacion': datetime.now().isoformat()
                }
                
                # Insertar nueva noticia
                return self.insertar_noticia_nueva(datos_insercion)
                
        except Exception as e:
            self._log_error(f"Error procesando noticia: {e}")
            return False

    def generar_hash_contenido(self, titulo: str, contenido: str, url: str) -> str:
        """Generar hash único para el contenido"""
        import hashlib
        contenido_para_hash = f"{titulo}|{contenido[:200]}|{url}"
        return hashlib.md5(contenido_para_hash.encode('utf-8')).hexdigest()
'''
        
        # Buscar donde insertar las funciones (antes del método scrape)
        if 'def scrape_noticias_recientes' in contenido_actual:
            # Insertar antes del método scrape
            contenido_mejorado = contenido_actual.replace(
                '    def scrape_noticias_recientes(self, max_noticias: int = 10) -> List[NoticiaEstandarizada]:',
                funciones_duplicados + '\n    def scrape_noticias_recientes(self, max_noticias: int = 10) -> List[NoticiaEstandarizada]:'
            )
        else:
            # Insertar al final de la clase
            contenido_mejorado = contenido_actual.replace(
                'class ContraloriaScraper(BaseScraper):',
                'class ContraloriaScraper(BaseScraper):' + funciones_duplicados
            )
        
        # Guardar el scraper mejorado
        with open('contraloria_scraper_mejorado.py', 'w') as f:
            f.write(contenido_mejorado)
        
        print("✅ Scraper mejorado creado: contraloria_scraper_mejorado.py")
        print("\n📋 **MEJORAS IMPLEMENTADAS:**")
        print("   - Verificación de noticias existentes por URL")
        print("   - Actualización de noticias existentes")
        print("   - Inserción de nuevas noticias")
        print("   - Generación de hash único mejorada")
        print("   - Manejo graceful de duplicados")
        
    except Exception as e:
        print(f"❌ Error creando scraper mejorado: {e}")

def probar_scraper_mejorado():
    """Probar el scraper mejorado"""
    print("\n🧪 **PRUEBA DEL SCRAPER MEJORADO**")
    print("=" * 60)
    
    try:
        # Importar y ejecutar el scraper mejorado
        from contraloria_scraper_mejorado import ContraloriaScraper
        
        scraper = ContraloriaScraper()
        noticias = scraper.scrape_noticias_recientes(max_noticias=3)
        
        if noticias:
            print(f"✅ Se extrajeron {len(noticias)} noticias")
            
            for i, noticia in enumerate(noticias[:2], 1):
                titulo = noticia.titulo if hasattr(noticia, 'titulo') else str(noticia)
                print(f"   {i}. {titulo[:50]}...")
        else:
            print("❌ No se extrajeron noticias")
            
    except ImportError:
        print("⚠️ Scraper mejorado no disponible, creando...")
        crear_scraper_contraloria_mejorado()
    except Exception as e:
        print(f"❌ Error probando scraper: {e}")

def main():
    """Función principal"""
    print("🔧 **INTEGRACIÓN DE SOLUCIÓN - CONTRALORÍA**")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Ejecutar integración
    crear_scraper_contraloria_mejorado()
    probar_scraper_mejorado()
    
    print(f"\n✅ **INTEGRACIÓN COMPLETADA**")
    print("=" * 70)

if __name__ == "__main__":
    main() 
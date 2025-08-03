#!/usr/bin/env python3
"""
Script para eliminar frases de cierre indeseadas del contenido de noticias
"""

import os
import sys
import re
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

# Agregar el directorio al path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.database.supabase_client import SupabaseClient

class LimpiadorFrasesCierre:
    def __init__(self):
        # Configurar Supabase
        self.supabase = SupabaseClient(
            url=os.getenv('SUPABASE_URL'),
            key=os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        )
        
        # Patrones de frases de cierre a eliminar
        self.patrones_cierre = [
            # Acceder al expediente
            r'Acceder al expediente de la causa[A-Z0-9\-]+',
            r'Acceder al expediente[A-Z0-9\-]+',
            
            # Direcciones y contactos del Tribunal Ambiental
            r'Morandé 360, Piso 8, Santiago\([0-9\s\+]+\)',
            r'\([0-9\s\+]+\)contacto@tribunalambiental\.cl',
            r'contacto@tribunalambiental\.cl',
            
            # Teléfonos duplicados
            r'Piso 8, Santiago\([0-9\s\+]+\)',
            r'\([0-9\s\+]+\), Piso 8, Santiago',
            
            # Patrones más generales de cierre institucional
            r'Morandé 360, Piso 8, Santiago.*$',
            r'\([0-9\s\+\-]+\).*@[a-zA-Z0-9\.\-]+\.[a-zA-Z]{2,}.*$',
        ]

    def limpiar_contenido(self, contenido: str) -> str:
        """Limpiar frases de cierre del contenido"""
        contenido_limpio = contenido
        
        # Aplicar cada patrón de limpieza
        for patron in self.patrones_cierre:
            contenido_limpio = re.sub(patron, '', contenido_limpio, flags=re.IGNORECASE | re.MULTILINE)
        
        # Limpiar espacios extras y puntos sueltos
        contenido_limpio = re.sub(r'\s+', ' ', contenido_limpio)  # Múltiples espacios
        contenido_limpio = re.sub(r'\.\s*\.\s*\.', '.', contenido_limpio)  # Puntos múltiples
        contenido_limpio = re.sub(r'\s+\.$', '.', contenido_limpio)  # Espacios antes del punto final
        
        return contenido_limpio.strip()

    def necesita_limpieza(self, contenido: str) -> bool:
        """Verificar si el contenido necesita limpieza"""
        frases_problema = [
            'Acceder al expediente',
            'Morandé 360',
            'contacto@tribunalambiental.cl',
            '2393 69 00'
        ]
        
        contenido_lower = contenido.lower()
        return any(frase.lower() in contenido_lower for frase in frases_problema)

    def procesar_noticia(self, noticia: Dict) -> bool:
        """Procesar una noticia individual"""
        noticia_id = noticia.get('id')
        contenido_original = noticia.get('cuerpo_completo', '')
        
        if not self.necesita_limpieza(contenido_original):
            return False
        
        contenido_limpio = self.limpiar_contenido(contenido_original)
        
        if contenido_limpio != contenido_original:
            return self.actualizar_noticia_en_supabase(noticia_id, contenido_limpio)
        
        return False

    def actualizar_noticia_en_supabase(self, noticia_id: str, contenido: str) -> bool:
        """Actualizar noticia en Supabase"""
        try:
            import requests
            
            url = f'{os.getenv("SUPABASE_URL")}/rest/v1/noticias_juridicas'
            headers = {
                'apikey': os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
                'Authorization': f'Bearer {os.getenv("SUPABASE_SERVICE_ROLE_KEY")}',
                'Content-Type': 'application/json',
                'Prefer': 'return=representation'
            }
            
            data = {'cuerpo_completo': contenido}
            response = requests.patch(
                f'{url}?id=eq.{noticia_id}',
                json=data,
                headers=headers
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Error actualizando noticia: {str(e)}")
            return False

    def procesar_todas_las_noticias(self, limite: int = None):
        """Procesar todas las noticias para limpiar frases de cierre"""
        print("🧹 INICIANDO LIMPIEZA DE FRASES DE CIERRE")
        print("========================================")
        
        # Obtener todas las noticias
        noticias = self.supabase.get_noticias_recientes(limit=limite or 1000)
        
        if not noticias:
            print("❌ No se encontraron noticias")
            return
        
        print(f"📊 Analizando {len(noticias)} noticias...")
        
        total_procesadas = 0
        total_limpiadas = 0
        errores = 0
        
        for i, noticia in enumerate(noticias, 1):
            titulo = noticia.get('titulo', '')[:60]
            
            try:
                if self.necesita_limpieza(noticia.get('cuerpo_completo', '')):
                    print(f"\n🧹 {i}/{len(noticias)}: {titulo}...")
                    
                    if self.procesar_noticia(noticia):
                        print(f"✅ Frases de cierre eliminadas")
                        total_limpiadas += 1
                    else:
                        print(f"❌ Error limpiando")
                        errores += 1
                else:
                    if i % 20 == 0:  # Mostrar progreso cada 20
                        print(f"📝 {i}/{len(noticias)}: Sin problemas de cierre")
                
                total_procesadas += 1
                
            except Exception as e:
                print(f"❌ Error procesando {titulo}: {str(e)}")
                errores += 1
        
        print(f"\n📊 RESUMEN FINAL:")
        print(f"📈 Total analizadas: {total_procesadas}")
        print(f"🧹 Limpiadas: {total_limpiadas}")
        print(f"❌ Errores: {errores}")

def main():
    """Función principal"""
    print("🧹 LIMPIADOR DE FRASES DE CIERRE")
    print("=================================")
    
    # Verificar variables de entorno
    if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_SERVICE_ROLE_KEY'):
        print("❌ Error: Variables de Supabase no configuradas")
        return
    
    limpiador = LimpiadorFrasesCierre()
    
    # Probar primero con las primeras noticias que tienen el problema
    print("🧪 MODO PRUEBA: Analizando noticias...")
    limpiador.procesar_todas_las_noticias(limite=50)
    
    respuesta = input("\n¿Continuar con todas las noticias? (s/n): ")
    if respuesta.lower() == 's':
        print("\n🚀 Procesando todas las noticias...")
        limpiador.procesar_todas_las_noticias()
    else:
        print("✅ Proceso detenido por el usuario")

if __name__ == "__main__":
    main() 
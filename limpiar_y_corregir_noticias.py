#!/usr/bin/env python3
"""
Script para limpiar duplicación de títulos y corregir fechas reales en noticias
"""

import os
import sys
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

# Agregar el directorio al path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.database.supabase_client import SupabaseClient

class LimpiadorNoticias:
    def __init__(self):
        # Configurar Supabase
        self.supabase = SupabaseClient(
            url=os.getenv('SUPABASE_URL'),
            key=os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        )
        
        # Diccionario para convertir meses
        self.meses = {
            'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
            'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
            'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
        }

    def extraer_fecha_real(self, contenido: str) -> Optional[str]:
        """Extraer la fecha real del contenido de la noticia"""
        try:
            # Buscar patrones de fecha en español: "13 junio 2025"
            patron_mes = r'(\d{1,2})\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+(\d{4})'
            match = re.search(patron_mes, contenido, re.IGNORECASE)
            
            if match:
                dia = match.group(1).zfill(2)
                mes_nombre = match.group(2).lower()
                año = match.group(3)
                mes_numero = self.meses.get(mes_nombre, '01')
                
                # Convertir a formato ISO
                fecha_iso = f"{año}-{mes_numero}-{dia}"
                
                # Validar que la fecha sea válida
                datetime.strptime(fecha_iso, '%Y-%m-%d')
                return fecha_iso
            
            # Buscar otros patrones de fecha
            patron_dd_mm_yyyy = r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})'
            match = re.search(patron_dd_mm_yyyy, contenido)
            if match:
                dia = match.group(1).zfill(2)
                mes = match.group(2).zfill(2)
                año = match.group(3)
                fecha_iso = f"{año}-{mes}-{dia}"
                
                # Validar que la fecha sea válida
                datetime.strptime(fecha_iso, '%Y-%m-%d')
                return fecha_iso
                
            return None
            
        except Exception as e:
            print(f"❌ Error extrayendo fecha: {str(e)}")
            return None

    def limpiar_duplicacion_titulo(self, titulo: str, contenido: str) -> str:
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
            palabras_titulo = titulo_limpio.split()[:7]  # Primeras 7 palabras del título
            if len(palabras_titulo) >= 4:
                inicio_titulo = ' '.join(palabras_titulo[:4])
                if contenido.lower().startswith(inicio_titulo.lower()):
                    # Encontrar donde termina el título en el contenido
                    try:
                        # Buscar el patrón: título + fecha + resto
                        patron_titulo_fecha = rf'{re.escape(titulo_limpio)}\s*\d{{1,2}}\s+\w+\s+\d{{4}}'
                        match = re.search(patron_titulo_fecha, contenido, re.IGNORECASE)
                        
                        if match:
                            contenido_limpio = contenido[match.end():].strip()
                        else:
                            # Método alternativo: buscar el final del título
                            fin_titulo = contenido.lower().find(titulo_limpio.lower()) + len(titulo_limpio)
                            resto = contenido[fin_titulo:]
                            
                            # Buscar el primer punto de corte natural después del título
                            cortes = [' 20', '. ', '\n', '  ']
                            for corte in cortes:
                                idx = resto.find(corte)
                                if idx >= 0 and idx < 150:  # Dentro de los primeros 150 caracteres
                                    contenido_limpio = resto[idx:].strip()
                                    if corte.strip():
                                        contenido_limpio = contenido_limpio[len(corte):].strip()
                                    break
                            else:
                                contenido_limpio = contenido
                    except:
                        contenido_limpio = contenido
                else:
                    contenido_limpio = contenido
            else:
                contenido_limpio = contenido
        
        # Eliminar fechas sueltas al inicio (formato DD mes YYYY)
        contenido_limpio = re.sub(r'^\d{1,2}\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+\d{4}\s*', '', contenido_limpio, flags=re.IGNORECASE)
        
        return contenido_limpio.strip()

    def procesar_noticia(self, noticia: Dict) -> Tuple[bool, Dict]:
        """Procesar una noticia individual"""
        noticia_id = noticia.get('id')
        titulo = noticia.get('titulo', '')
        contenido_original = noticia.get('cuerpo_completo', '')
        fecha_actual = noticia.get('fecha_publicacion', '')
        
        cambios = {}
        hubo_cambios = False
        
        # 1. Limpiar duplicación del título
        contenido_limpio = self.limpiar_duplicacion_titulo(titulo, contenido_original)
        
        if contenido_limpio != contenido_original:
            cambios['cuerpo_completo'] = contenido_limpio
            hubo_cambios = True
            print(f"   🧹 Título duplicado removido")
        
        # 2. Extraer fecha real
        fecha_real = self.extraer_fecha_real(contenido_original)
        
        if fecha_real and fecha_real != fecha_actual[:10]:  # Comparar solo la parte de fecha
            cambios['fecha_publicacion'] = fecha_real + 'T00:00:00+00:00'
            hubo_cambios = True
            print(f"   📅 Fecha corregida: {fecha_actual[:10]} → {fecha_real}")
        
        return hubo_cambios, cambios

    def actualizar_noticia_en_supabase(self, noticia_id: str, cambios: Dict) -> bool:
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
            
            response = requests.patch(
                f'{url}?id=eq.{noticia_id}',
                json=cambios,
                headers=headers
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Error actualizando noticia: {str(e)}")
            return False

    def procesar_todas_las_noticias(self, limite: int = None):
        """Procesar todas las noticias para limpiar y corregir"""
        print("🚀 INICIANDO LIMPIEZA Y CORRECCIÓN DE NOTICIAS")
        print("==============================================")
        
        # Obtener todas las noticias
        noticias = self.supabase.get_noticias_recientes(limit=limite or 1000)
        
        if not noticias:
            print("❌ No se encontraron noticias")
            return
        
        print(f"📊 Procesando {len(noticias)} noticias...")
        
        exitosos = 0
        con_cambios = 0
        errores = 0
        
        for i, noticia in enumerate(noticias, 1):
            titulo = noticia.get('titulo', '')[:60]
            print(f"\n📝 {i}/{len(noticias)}: {titulo}...")
            
            try:
                hubo_cambios, cambios = self.procesar_noticia(noticia)
                
                if hubo_cambios:
                    if self.actualizar_noticia_en_supabase(noticia['id'], cambios):
                        print(f"✅ Actualizada correctamente")
                        con_cambios += 1
                    else:
                        print(f"❌ Error actualizando en Supabase")
                        errores += 1
                else:
                    print(f"ℹ️ Sin cambios necesarios")
                
                exitosos += 1
                
            except Exception as e:
                print(f"❌ Error procesando: {str(e)}")
                errores += 1
        
        print(f"\n📊 RESUMEN FINAL:")
        print(f"✅ Procesadas: {exitosos}")
        print(f"🔄 Con cambios: {con_cambios}")
        print(f"❌ Errores: {errores}")

def main():
    """Función principal"""
    print("🎯 LIMPIADOR Y CORRECTOR DE NOTICIAS")
    print("====================================")
    
    # Verificar variables de entorno
    if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_SERVICE_ROLE_KEY'):
        print("❌ Error: Variables de Supabase no configuradas")
        return
    
    limpiador = LimpiadorNoticias()
    
    # Probar primero con 3 noticias
    print("🧪 MODO PRUEBA: Procesando las primeras 3 noticias...")
    limpiador.procesar_todas_las_noticias(limite=3)
    
    respuesta = input("\n¿Continuar con todas las noticias? (s/n): ")
    if respuesta.lower() == 's':
        print("\n🚀 Procesando todas las noticias...")
        limpiador.procesar_todas_las_noticias()
    else:
        print("✅ Proceso detenido por el usuario")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Script para generar resúmenes ejecutivos de 6 líneas para todas las noticias existentes
usando GPT-3.5 Turbo y actualizar Supabase.
"""

import os
import sys
import time
from typing import List, Dict
import openai
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

# Agregar el directorio al path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.database.supabase_client import SupabaseClient

class ResumenEjecutivoGenerator:
    def __init__(self):
        # Configurar OpenAI
        self.client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Configurar Supabase
        self.supabase = SupabaseClient(
            url=os.getenv('SUPABASE_URL'),
            key=os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        )
        
        # Prompt optimizado para resúmenes ejecutivos
        self.prompt_template = """Eres un experto en comunicación jurídica. Genera un resumen ejecutivo de exactamente 6 líneas que:

1. Complemente (no repita) el título proporcionado
2. Explique el núcleo central de la noticia
3. Sea autocontenido para que el lector no necesite leer más
4. Use lenguaje profesional pero accesible
5. Incluya los datos más relevantes (fechas, montos, personas, consecuencias)
6. Cada línea debe ser sustancial y aportar información valiosa

Título: {titulo}

Contenido: {contenido}

Genera un resumen ejecutivo de exactamente 6 líneas (sin numeración, solo párrafo corrido):"""

    def obtener_noticias_sin_resumen(self) -> List[Dict]:
        """Obtener noticias que no tienen resumen ejecutivo o tienen resumen corto"""
        try:
            # Usar el método de búsqueda disponible 
            response = self.supabase.get_noticias_recientes(limit=1000)
            
            # Filtrar noticias sin resumen o con resumen muy corto
            noticias_filtradas = []
            for noticia in response:
                resumen = noticia.get('resumen_ejecutivo', '')
                if not resumen or len(resumen) < 200:
                    noticias_filtradas.append(noticia)
            
            print(f"📊 Encontradas {len(noticias_filtradas)} noticias para generar resúmenes")
            return noticias_filtradas
                
        except Exception as e:
            print(f"❌ Error obteniendo noticias: {str(e)}")
            return []

    def generar_resumen_ejecutivo(self, titulo: str, contenido: str) -> str:
        """Generar resumen ejecutivo usando GPT-3.5 Turbo"""
        try:
            # Limpiar y truncar contenido si es muy largo
            contenido_limpio = contenido.replace('\n', ' ').strip()
            if len(contenido_limpio) > 3000:
                contenido_limpio = contenido_limpio[:3000] + "..."
            
            prompt = self.prompt_template.format(
                titulo=titulo,
                contenido=contenido_limpio
            )
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un experto en comunicación jurídica que genera resúmenes ejecutivos precisos y concisos."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3,
                top_p=0.9
            )
            
            resumen = response.choices[0].message.content.strip()
            
            # Validar que tenga aproximadamente 6 líneas (entre 400-800 caracteres)
            if len(resumen) < 200:
                print(f"⚠️ Resumen muy corto ({len(resumen)} chars), regenerando...")
                return self.generar_resumen_ejecutivo(titulo, contenido)
            
            return resumen
            
        except Exception as e:
            print(f"❌ Error generando resumen: {str(e)}")
            return ""

    def actualizar_resumen_en_supabase(self, noticia_id: str, resumen: str) -> bool:
        """Actualizar el resumen en Supabase usando requests directo"""
        try:
            import requests
            
            url = f'{os.getenv("SUPABASE_URL")}/rest/v1/noticias_juridicas'
            headers = {
                'apikey': os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
                'Authorization': f'Bearer {os.getenv("SUPABASE_SERVICE_ROLE_KEY")}',
                'Content-Type': 'application/json',
                'Prefer': 'return=representation'
            }
            
            data = {'resumen_ejecutivo': resumen}
            response = requests.patch(
                f'{url}?id=eq.{noticia_id}',
                json=data,
                headers=headers
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Error actualizando resumen en Supabase: {str(e)}")
            return False

    def procesar_todas_las_noticias(self):
        """Procesar todas las noticias para generar resúmenes ejecutivos"""
        print("🚀 Iniciando generación de resúmenes ejecutivos...")
        
        noticias = self.obtener_noticias_sin_resumen()
        if not noticias:
            print("✅ No hay noticias para procesar")
            return
        
        exitosos = 0
        errores = 0
        
        for i, noticia in enumerate(noticias, 1):
            titulo = noticia.get('titulo', '')
            contenido = noticia.get('cuerpo_completo', '')
            noticia_id = noticia.get('id', '')
            
            print(f"\n📝 Procesando {i}/{len(noticias)}: {titulo[:60]}...")
            
            if not titulo or not contenido or not noticia_id:
                print(f"❌ Datos incompletos para la noticia")
                errores += 1
                continue
            
            try:
                # Generar resumen ejecutivo
                resumen = self.generar_resumen_ejecutivo(titulo, contenido)
                
                if resumen:
                    # Actualizar en Supabase
                    if self.actualizar_resumen_en_supabase(noticia_id, resumen):
                        print(f"✅ Resumen generado y guardado ({len(resumen)} chars)")
                        exitosos += 1
                    else:
                        print(f"❌ Error guardando resumen")
                        errores += 1
                else:
                    print(f"❌ No se pudo generar resumen")
                    errores += 1
                
                # Pausa para no sobrecargar la API
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error procesando noticia: {str(e)}")
                errores += 1
        
        print(f"\n📊 RESUMEN FINAL:")
        print(f"✅ Exitosos: {exitosos}")
        print(f"❌ Errores: {errores}")
        print(f"📈 Total procesadas: {len(noticias)}")

def main():
    """Función principal"""
    print("🎯 GENERADOR DE RESÚMENES EJECUTIVOS")
    print("=====================================")
    
    # Verificar variables de entorno
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY no configurada")
        return
    
    if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_SERVICE_ROLE_KEY'):
        print("❌ Error: Variables de Supabase no configuradas")
        return
    
    generator = ResumenEjecutivoGenerator()
    generator.procesar_todas_las_noticias()

if __name__ == "__main__":
    main() 
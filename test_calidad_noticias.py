#!/usr/bin/env python3
"""
Script para probar la calidad de las noticias antes de subir todo
Verifica: 1) No basura, 2) Títulos limpios, 3) Resumen IA completo
"""

import sys
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.scrapers.fuentes.contraloria.contraloria_scraper import ContraloriaScraper
from backend.scrapers.fuentes.cde.cde_scraper import CDEScraper
from backend.scrapers.fuentes.poder_judicial.poder_judicial_scraper_v2 import PoderJudicialScraperV2
from backend.processors.content_processor import ContentProcessor

def test_calidad_noticias():
    """Probar calidad de noticias antes de subir todo"""
    print("🧪 **TEST DE CALIDAD DE NOTICIAS**")
    print("=" * 50)
    print("Verificando: 1) No basura, 2) Títulos limpios, 3) Resumen IA completo")
    print("=" * 50)
    
    # Inicializar procesador de contenido
    processor = ContentProcessor(openai_api_key=os.getenv('OPENAI_API_KEY'))
    
    # Probar con diferentes fuentes
    fuentes_test = [
        ('contraloria', ContraloriaScraper()),
        ('cde', CDEScraper()),
        ('poder_judicial', PoderJudicialScraperV2())
    ]
    
    resultados = {}
    
    for fuente_nombre, scraper in fuentes_test:
        print(f"\n📰 **PROBANDO {fuente_nombre.upper()}**")
        print("-" * 30)
        
        try:
            # Obtener 2 noticias de prueba
            noticias = scraper.scrape_noticias_recientes(max_noticias=2)
            
            if not noticias:
                print(f"❌ No se obtuvieron noticias de {fuente_nombre}")
                continue
            
            fuente_resultados = []
            
            for i, noticia in enumerate(noticias, 1):
                print(f"\n  📄 Noticia {i}:")
                
                # 1. Verificar título limpio
                titulo_original = noticia.titulo
                titulo_limpio = processor._limpiar_titulo(titulo_original)
                
                print(f"    📝 Título original: {titulo_original[:80]}...")
                print(f"    ✨ Título limpio: {titulo_limpio[:80]}...")
                
                # Verificar si se limpió correctamente
                if titulo_original != titulo_limpio:
                    print(f"    ✅ Título limpiado correctamente")
                else:
                    print(f"    ⚠️  Título no necesitaba limpieza")
                
                # 2. Verificar contenido limpio
                contenido_original = noticia.cuerpo_completo
                contenido_limpio = processor._limpiar_contenido(contenido_original)
                
                print(f"    📄 Contenido: {len(contenido_original)} → {len(contenido_limpio)} caracteres")
                
                # 3. Generar resumen ejecutivo con IA
                print(f"    🤖 Generando resumen ejecutivo...")
                resumen = processor.generar_resumen_ejecutivo(
                    titulo_limpio, 
                    contenido_limpio, 
                    fuente_nombre
                )
                
                if resumen and 'resumen_contenido' in resumen:
                    resumen_texto = resumen['resumen_contenido']
                    print(f"    📋 Resumen: {resumen_texto[:100]}...")
                    print(f"    📊 Longitud: {len(resumen_texto)} caracteres")
                    
                    # Verificar calidad del resumen
                    if len(resumen_texto) > 50 and len(resumen_texto) < 500:
                        print(f"    ✅ Resumen de calidad adecuada")
                    else:
                        print(f"    ⚠️  Resumen muy corto o muy largo")
                else:
                    print(f"    ❌ Error generando resumen")
                
                # 4. Verificar que no es basura
                es_basura = _verificar_basura(titulo_limpio, contenido_limpio)
                if not es_basura:
                    print(f"    ✅ Contenido relevante")
                else:
                    print(f"    ❌ Posible contenido irrelevante")
                
                # Guardar resultado
                fuente_resultados.append({
                    'titulo_original': titulo_original,
                    'titulo_limpio': titulo_limpio,
                    'contenido_limpio': contenido_limpio,
                    'resumen': resumen,
                    'es_basura': es_basura
                })
            
            resultados[fuente_nombre] = fuente_resultados
            
        except Exception as e:
            print(f"❌ Error probando {fuente_nombre}: {e}")
            continue
    
    # Mostrar resumen final
    print(f"\n📊 **RESUMEN DE CALIDAD**")
    print("=" * 50)
    
    total_noticias = 0
    titulos_limpios = 0
    resumenes_ok = 0
    contenido_relevante = 0
    
    for fuente, noticias in resultados.items():
        print(f"\n📰 {fuente.upper()}: {len(noticias)} noticias")
        
        for noticia in noticias:
            total_noticias += 1
            
            if noticia['titulo_original'] != noticia['titulo_limpio']:
                titulos_limpios += 1
            
            if noticia['resumen'] and 'resumen_contenido' in noticia['resumen']:
                resumen_len = len(noticia['resumen']['resumen_contenido'])
                if 50 < resumen_len < 500:
                    resumenes_ok += 1
            
            if not noticia['es_basura']:
                contenido_relevante += 1
    
    print(f"\n🎯 **ESTADÍSTICAS GENERALES**")
    print(f"   📊 Total noticias probadas: {total_noticias}")
    print(f"   ✨ Títulos limpiados: {titulos_limpios}/{total_noticias} ({titulos_limpios/total_noticias*100:.1f}%)")
    print(f"   🤖 Resúmenes de calidad: {resumenes_ok}/{total_noticias} ({resumenes_ok/total_noticias*100:.1f}%)")
    print(f"   ✅ Contenido relevante: {contenido_relevante}/{total_noticias} ({contenido_relevante/total_noticias*100:.1f}%)")
    
    # Recomendación
    if resumenes_ok/total_noticias > 0.8 and contenido_relevante/total_noticias > 0.9:
        print(f"\n✅ **CALIDAD ACEPTABLE - LISTO PARA SUBIR**")
        return True
    else:
        print(f"\n⚠️  **PROBLEMAS DE CALIDAD DETECTADOS**")
        print(f"   Se recomienda revisar antes de subir")
        return False

def _verificar_basura(titulo: str, contenido: str) -> bool:
    """Verificar si el contenido es basura/irrelevante"""
    # Palabras que indican contenido irrelevante
    palabras_basura = [
        'error', 'página no encontrada', '404', 'acceso denegado',
        'mantenimiento', 'temporalmente no disponible', 'en construcción',
        'próximamente', 'coming soon', 'under construction'
    ]
    
    texto_completo = (titulo + ' ' + contenido).lower()
    
    for palabra in palabras_basura:
        if palabra in texto_completo:
            return True
    
    # Verificar contenido muy corto
    if len(contenido.strip()) < 50:
        return True
    
    return False

if __name__ == "__main__":
    calidad_ok = test_calidad_noticias()
    
    if calidad_ok:
        print(f"\n🚀 **LISTO PARA CONTINUAR CON LA EXTRACCIÓN COMPLETA**")
    else:
        print(f"\n🔧 **SE RECOMIENDA REVISAR ANTES DE CONTINUAR**") 
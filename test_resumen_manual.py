#!/usr/bin/env python3
"""
Script para probar el nuevo sistema de resumen manual (primer párrafo + ...)
"""

import sys
import os
from backend.processors.content_processor import ContentProcessor

def test_resumen_manual():
    """Probar el sistema de resumen manual"""
    
    print("🧪 PROBANDO SISTEMA DE RESUMEN MANUAL")
    print("=" * 60)
    
    # Crear processor sin IA
    processor = ContentProcessor(openai_api_key=None)
    
    # Ejemplos de contenido para probar
    ejemplos = [
        {
            "titulo": "Corte Suprema confirma sentencia en caso de corrupción",
            "contenido": "Corte Suprema confirma sentencia en caso de corrupción. La Corte Suprema confirmó la sentencia del tribunal de primera instancia en un caso que ha generado gran interés público. El fallo establece precedentes importantes para futuros casos similares y refuerza la lucha contra la corrupción en el país. Los magistrados consideraron que las pruebas presentadas eran suficientes para mantener la condena.",
            "fuente": "poder_judicial"
        },
        {
            "titulo": "Ministerio de Justicia presenta nueva política de transparencia",
            "contenido": "Ministerio de Justicia presenta nueva política de transparencia. El Ministerio de Justicia presentó una nueva política de transparencia que mejorará el acceso a la información pública. Esta iniciativa busca fortalecer la confianza ciudadana en las instituciones del Estado y promover una mayor participación ciudadana en los procesos de toma de decisiones.",
            "fuente": "ministerio_justicia"
        },
        {
            "titulo": "Juzgado de Chaitén y Servicio de Protección a la Niñez evalúan coordinaciones con programas ambulatorios01-08-2025 04:08",
            "contenido": "Juzgado de Chaitén y Servicio de Protección a la Niñez evalúan coordinaciones con programas ambulatorios 01-agosto-2025. El encuentro, que se realizó en dependencias del tribunal, tuvo por finalidad establecer mecanismos de coordinación entre el Juzgado de Familia de Chaitén y el Servicio de Protección a la Niñez para mejorar la atención de casos que requieren intervención ambulatoria.",
            "fuente": "poder_judicial"
        }
    ]
    
    for i, ejemplo in enumerate(ejemplos, 1):
        print(f"\n📄 EJEMPLO {i}:")
        print(f"Título: {ejemplo['titulo']}")
        print(f"Fuente: {ejemplo['fuente']}")
        print(f"Contenido original: {ejemplo['contenido'][:100]}...")
        
        # Generar resumen
        resumen = processor.generar_resumen_ejecutivo(
            ejemplo['titulo'], 
            ejemplo['contenido'], 
            ejemplo['fuente']
        )
        
        print(f"\n✅ RESUMEN GENERADO:")
        print(f"Título limpio: {resumen['titulo_resumen']}")
        print(f"Resumen: {resumen['resumen_contenido']}")
        print(f"Longitud: {len(resumen['resumen_contenido'])} caracteres")
        print(f"Palabras clave: {resumen['palabras_clave']}")
        print("-" * 40)

def test_con_contenido_largo():
    """Probar con contenido más largo para verificar el límite de 400 caracteres"""
    
    print("\n🧪 PROBANDO CON CONTENIDO LARGO")
    print("=" * 60)
    
    processor = ContentProcessor(openai_api_key=None)
    
    contenido_largo = """
    La Corte Suprema de Chile emitió un fallo histórico que establece nuevos precedentes en materia de derechos constitucionales. El caso, que involucraba a múltiples partes y contó con la participación de expertos internacionales, ha sido seguido de cerca por la comunidad jurídica nacional e internacional.
    
    Los magistrados consideraron diversos aspectos del derecho comparado y analizaron jurisprudencia de otros países para llegar a su decisión final. El fallo incluye consideraciones sobre la interpretación constitucional y el balance entre diferentes derechos fundamentales.
    
    Esta sentencia tendrá implicaciones significativas para futuros casos similares y establece un marco claro para la interpretación de ciertas disposiciones constitucionales que habían sido objeto de debate en la doctrina jurídica.
    """
    
    resumen = processor.generar_resumen_ejecutivo(
        "Corte Suprema emite fallo histórico sobre derechos constitucionales",
        contenido_largo,
        "poder_judicial"
    )
    
    print(f"✅ RESUMEN DE CONTENIDO LARGO:")
    print(f"Resumen: {resumen['resumen_contenido']}")
    print(f"Longitud: {len(resumen['resumen_contenido'])} caracteres")
    print(f"¿Termina con (...)?: {'(...)' in resumen['resumen_contenido']}")

def test_limpieza_titulos():
    """Probar la limpieza de títulos con fechas pegadas"""
    
    print("\n🧪 PROBANDO LIMPIEZA DE TÍTULOS")
    print("=" * 60)
    
    processor = ContentProcessor(openai_api_key=None)
    
    titulos_problematicos = [
        "Juzgado de Chaitén y Servicio de Protección a la Niñez evalúan coordinaciones con programas ambulatorios01-08-2025 04:08",
        "Corte de Valparaíso informa plan de trabajo especial26-07-2025 04:07",
        "Fiscalía Regional logra importante condena en caso de corrupción15-06-2025 14:30",
        "Portal Unificado de Sentencias actualiza sistema de consultas30-05-2025 09:15"
    ]
    
    for titulo in titulos_problematicos:
        titulo_limpio = processor._limpiar_titulo(titulo)
        print(f"Título original: {titulo}")
        print(f"Título limpio: {titulo_limpio}")
        print("-" * 40)

if __name__ == "__main__":
    test_resumen_manual()
    test_con_contenido_largo()
    test_limpieza_titulos()
    
    print(f"\n🎉 PRUEBA COMPLETADA")
    print("El sistema ahora usa:")
    print("- Primer párrafo (400 caracteres) + (...)")
    print("- Sin repetir el título en el contenido")
    print("- Títulos limpios sin fechas pegadas") 
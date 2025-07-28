#!/usr/bin/env python3
"""
Script para probar optimizaciones de IA y medir ahorro de tokens
"""

import os
import time
from dotenv import load_dotenv
from backend.processors.content_processor import ContentProcessor

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

def test_optimizacion_ia():
    """Probar optimizaciones de IA"""
    print("🧪 **TEST DE OPTIMIZACIÓN IA**")
    print("=" * 50)
    
    # Inicializar procesador
    processor = ContentProcessor(os.getenv('OPENAI_API_KEY'))
    
    # Noticia de prueba
    titulo = "Corte de Apelaciones de Santiago confirma sentencia de 5 años por estafa"
    contenido = """
    La Corte de Apelaciones de Santiago confirmó la sentencia de 5 años de presidio 
    para el acusado por el delito de estafa. El tribunal rechazó los argumentos de 
    la defensa y mantuvo la condena original dictada por el Juzgado de Garantía.
    
    El recurso de apelación fue presentado por la defensa del imputado, quien 
    argumentaba que no se habían acreditado todos los elementos del tipo penal. 
    Sin embargo, la Corte consideró que la sentencia estaba correctamente fundada 
    y que se habían cumplido todos los requisitos legales.
    
    La sentencia confirma la condena de 5 años de presidio menor en su grado máximo 
    y el pago de una multa de 10 UTM. El fallo es inapelable y deberá cumplirse 
    en un recinto penitenciario.
    """
    fuente = "poder_judicial"
    
    print("📊 **PRUEBA 1: Primera llamada (sin cache)**")
    print("-" * 40)
    
    start_time = time.time()
    resultado1 = processor.generar_resumen_ejecutivo(titulo, contenido, fuente)
    tiempo1 = time.time() - start_time
    
    print(f"⏱️  Tiempo: {tiempo1:.2f} segundos")
    print(f"📝 Resumen: {resultado1.get('resumen_contenido', '')[:100]}...")
    print(f"🏷️  Palabras clave: {resultado1.get('palabras_clave', [])}")
    
    print("\n📊 **PRUEBA 2: Segunda llamada (con cache)**")
    print("-" * 40)
    
    start_time = time.time()
    resultado2 = processor.generar_resumen_ejecutivo(titulo, contenido, fuente)
    tiempo2 = time.time() - start_time
    
    print(f"⏱️  Tiempo: {tiempo2:.2f} segundos")
    print(f"📝 Resumen: {resultado2.get('resumen_contenido', '')[:100]}...")
    print(f"🏷️  Palabras clave: {resultado2.get('palabras_clave', [])}")
    
    print("\n📊 **COMPARACIÓN**")
    print("-" * 40)
    print(f"🔄 Primera llamada: {tiempo1:.2f}s")
    print(f"⚡ Segunda llamada: {tiempo2:.2f}s")
    print(f"💰 Ahorro de tiempo: {((tiempo1 - tiempo2) / tiempo1 * 100):.1f}%")
    print(f"🎯 Cache funcionando: {'✅' if tiempo2 < 0.1 else '❌'}")
    
    print("\n📋 **OPTIMIZACIONES IMPLEMENTADAS:**")
    print("✅ Cambio a GPT-3.5-turbo (más barato)")
    print("✅ Reducción de max_tokens: 800 → 300")
    print("✅ Reducción de contenido: 1500 → 800 caracteres")
    print("✅ Prompt más corto y directo")
    print("✅ Cache para evitar llamadas repetidas")
    print("✅ Temperature reducido: 0.3 → 0.2")
    
    print("\n💰 **ESTIMACIÓN DE AHORRO:**")
    print("• GPT-4 → GPT-3.5-turbo: ~90% más barato")
    print("• Tokens reducidos: ~60% menos")
    print("• Cache: 100% ahorro en llamadas repetidas")
    print("• Total estimado: ~95% de ahorro en costos")

if __name__ == "__main__":
    test_optimizacion_ia() 
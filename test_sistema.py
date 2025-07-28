#!/usr/bin/env python3
"""
Script de prueba para verificar el sistema de noticias jurídicas
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

def test_supabase_connection():
    """Probar conexión a Supabase"""
    print("🔍 Probando conexión a Supabase...")
    
    try:
        from backend.database.supabase_client import SupabaseClient
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Error: Faltan credenciales de Supabase")
            return False
        
        client = SupabaseClient(supabase_url, supabase_key)
        
        if client.test_connection():
            print("✅ Conexión a Supabase exitosa")
            return True
        else:
            print("❌ Error de conexión a Supabase")
            return False
            
    except Exception as e:
        print(f"❌ Error probando conexión: {e}")
        return False

def test_scraper():
    """Probar scraper del Poder Judicial"""
    print("\n🔍 Probando scraper del Poder Judicial...")
    
    try:
        from backend.scrapers.poder_judicial_scraper import PoderJudicialScraper
        
        scraper = PoderJudicialScraper(openai_api_key=os.getenv('OPENAI_API_KEY'))
        
        # Probar obtención de noticias recientes
        noticias_links = scraper.get_noticias_recientes(3)
        
        if noticias_links:
            print(f"✅ Encontradas {len(noticias_links)} noticias")
            
            # Probar extracción de una noticia
            primera_noticia = noticias_links[0]
            print(f"📄 Probando extracción: {primera_noticia['titulo'][:50]}...")
            
            noticia_completa = scraper.get_noticia_completa(
                primera_noticia['url'],
                primera_noticia['titulo']
            )
            
            if noticia_completa:
                print("✅ Noticia extraída exitosamente")
                print(f"   Título: {noticia_completa.titulo}")
                print(f"   Contenido: {len(noticia_completa.cuerpo_completo)} caracteres")
                return True
            else:
                print("❌ Error extrayendo noticia")
                return False
        else:
            print("❌ No se encontraron noticias")
            return False
            
    except Exception as e:
        print(f"❌ Error probando scraper: {e}")
        return False

def test_content_processor():
    """Probar procesador de contenido"""
    print("\n🔍 Probando procesador de contenido...")
    
    try:
        from backend.processors.content_processor import ContentProcessor, NoticiaCompleta
        from datetime import datetime, timezone
        
        processor = ContentProcessor(openai_api_key=os.getenv('OPENAI_API_KEY'))
        
        # Crear noticia de prueba
        noticia = NoticiaCompleta(
            titulo="Test: Corte Suprema emite fallo importante",
            titulo_original="Test: Corte Suprema emite fallo importante",
            cuerpo_completo="La Corte Suprema ha emitido un fallo importante que establece jurisprudencia en materia de derecho civil. El caso involucraba una disputa sobre propiedad intelectual y el tribunal estableció criterios claros para futuros casos similares.",
            fecha_publicacion=datetime.now(timezone.utc),
            fuente='poder_judicial',
            fuente_nombre_completo='Poder Judicial de Chile',
            url_origen='https://www.pjud.cl/test'
        )
        
        # Generar resumen
        resumen = processor.generate_resumen_juridico(noticia)
        
        if resumen:
            print("✅ Resumen generado exitosamente")
            print(f"   Título: {resumen.get('titulo_resumen', 'N/A')}")
            print(f"   Contenido: {len(resumen.get('resumen_contenido', ''))} caracteres")
            return True
        else:
            print("❌ Error generando resumen")
            return False
            
    except Exception as e:
        print(f"❌ Error probando procesador: {e}")
        return False

def test_database_operations():
    """Probar operaciones de base de datos"""
    print("\n🔍 Probando operaciones de base de datos...")
    
    try:
        from backend.database.supabase_client import SupabaseClient
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        client = SupabaseClient(supabase_url, supabase_key)
        
        # Probar contar noticias
        total_noticias = client.count_noticias()
        print(f"✅ Total noticias en BD: {total_noticias}")
        
        # Probar obtener noticias recientes
        noticias = client.get_noticias_recientes(5)
        print(f"✅ Noticias recientes obtenidas: {len(noticias)}")
        
        # Probar obtener fuentes
        fuentes = client.get_fuentes_activas()
        print(f"✅ Fuentes activas: {len(fuentes)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando base de datos: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 Iniciando pruebas del sistema de noticias jurídicas")
    print("=" * 60)
    
    tests = [
        ("Conexión Supabase", test_supabase_connection),
        ("Scraper Poder Judicial", test_scraper),
        ("Procesador de Contenido", test_content_processor),
        ("Operaciones BD", test_database_operations)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen de resultados
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El sistema está funcionando correctamente.")
        print("\n📋 Próximos pasos:")
        print("1. Ejecutar el sistema completo: python3 backend/main.py --once")
        print("2. Abrir noticias.html en el navegador")
        print("3. Verificar que las noticias se cargan correctamente")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
        print("\n🔧 Posibles soluciones:")
        print("1. Verificar credenciales en APIS_Y_CREDENCIALES.env")
        print("2. Crear las tablas en Supabase usando schema_supabase.sql")
        print("3. Instalar dependencias: pip install -r requirements.txt")

if __name__ == "__main__":
    main() 
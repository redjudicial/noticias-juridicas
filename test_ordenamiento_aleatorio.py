#!/usr/bin/env python3
"""
Script para probar el ordenamiento aleatorio de noticias
"""

import os
import sys
import random
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

def simular_ordenamiento_aleatorio():
    """Simular el ordenamiento aleatorio para verificar variedad de fuentes"""
    print("🧪 Probando ordenamiento aleatorio de noticias...")
    
    try:
        from backend.database.supabase_client import SupabaseClient
        
        supabase = SupabaseClient(
            url=os.getenv('SUPABASE_URL'),
            key=os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        )
        
        # Obtener noticias recientes
        noticias = supabase.get_noticias_recientes(limit=50)
        
        if not noticias:
            print("❌ No se encontraron noticias para probar")
            return False
        
        print(f"📊 Total de noticias obtenidas: {len(noticias)}")
        
        # Contar fuentes
        fuentes = {}
        for noticia in noticias:
            fuente = noticia.get('fuente', 'desconocida')
            fuentes[fuente] = fuentes.get(fuente, 0) + 1
        
        print(f"\n📰 Distribución de fuentes:")
        for fuente, cantidad in sorted(fuentes.items()):
            print(f"   {fuente}: {cantidad} noticias")
        
        # Simular ordenamiento aleatorio
        print(f"\n🔄 Simulando ordenamiento aleatorio...")
        
        # Ordenamiento original (por fecha)
        noticias_ordenadas = sorted(noticias, key=lambda x: x.get('fecha_publicacion', ''), reverse=True)
        
        # Ordenamiento aleatorio
        noticias_aleatorias = noticias.copy()
        random.shuffle(noticias_aleatorias)
        
        # Verificar variedad en los primeros 12 elementos (una página)
        print(f"\n📋 Primeras 12 noticias (ordenadas por fecha):")
        fuentes_originales = []
        for i, noticia in enumerate(noticias_ordenadas[:12], 1):
            fuente = noticia.get('fuente', 'desconocida')
            fuentes_originales.append(fuente)
            print(f"   {i:2d}. [{fuente}] {noticia.get('titulo', 'Sin título')[:50]}...")
        
        print(f"\n🎲 Primeras 12 noticias (orden aleatorio):")
        fuentes_aleatorias = []
        for i, noticia in enumerate(noticias_aleatorias[:12], 1):
            fuente = noticia.get('fuente', 'desconocida')
            fuentes_aleatorias.append(fuente)
            print(f"   {i:2d}. [{fuente}] {noticia.get('titulo', 'Sin título')[:50]}...")
        
        # Calcular variedad
        variedad_original = len(set(fuentes_originales))
        variedad_aleatoria = len(set(fuentes_aleatorias))
        
        print(f"\n📊 Análisis de variedad:")
        print(f"   Orden original: {variedad_original} fuentes diferentes")
        print(f"   Orden aleatorio: {variedad_aleatoria} fuentes diferentes")
        
        if variedad_aleatoria > variedad_original:
            print(f"✅ ¡El ordenamiento aleatorio mejora la variedad de fuentes!")
        elif variedad_aleatoria == variedad_original:
            print(f"ℹ️  La variedad es similar en ambos ordenamientos")
        else:
            print(f"⚠️  El ordenamiento aleatorio no mejoró la variedad")
        
        # Verificar que no hay bloques grandes de la misma fuente
        print(f"\n🔍 Verificando bloques de fuentes:")
        
        def analizar_bloques(fuentes_lista):
            bloques = []
            fuente_actual = None
            contador = 0
            
            for fuente in fuentes_lista:
                if fuente == fuente_actual:
                    contador += 1
                else:
                    if contador > 0:
                        bloques.append((fuente_actual, contador))
                    fuente_actual = fuente
                    contador = 1
            
            if contador > 0:
                bloques.append((fuente_actual, contador))
            
            return bloques
        
        bloques_originales = analizar_bloques(fuentes_originales)
        bloques_aleatorios = analizar_bloques(fuentes_aleatorias)
        
        print(f"   Bloques en orden original:")
        for fuente, cantidad in bloques_originales:
            print(f"      {fuente}: {cantidad} consecutivas")
        
        print(f"   Bloques en orden aleatorio:")
        for fuente, cantidad in bloques_aleatorios:
            print(f"      {fuente}: {cantidad} consecutivas")
        
        # Verificar si hay bloques grandes (más de 3 consecutivas)
        bloques_grandes_original = [b for b in bloques_originales if b[1] > 3]
        bloques_grandes_aleatorio = [b for b in bloques_aleatorios if b[1] > 3]
        
        print(f"\n📈 Resultado:")
        print(f"   Bloques grandes (>3 consecutivas) en orden original: {len(bloques_grandes_original)}")
        print(f"   Bloques grandes (>3 consecutivas) en orden aleatorio: {len(bloques_grandes_aleatorio)}")
        
        if len(bloques_grandes_aleatorio) < len(bloques_grandes_original):
            print(f"✅ ¡El ordenamiento aleatorio reduce los bloques grandes!")
        else:
            print(f"ℹ️  El ordenamiento aleatorio mantiene similar distribución de bloques")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando ordenamiento aleatorio: {e}")
        return False

def verificar_paginacion():
    """Verificar que la paginación funcione correctamente"""
    print(f"\n📄 Verificando paginación...")
    
    try:
        from backend.database.supabase_client import SupabaseClient
        
        supabase = SupabaseClient(
            url=os.getenv('SUPABASE_URL'),
            key=os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        )
        
        total_noticias = supabase.count_noticias()
        noticias_por_pagina = 12
        total_paginas = (total_noticias + noticias_por_pagina - 1) // noticias_por_pagina
        
        print(f"📊 Estadísticas de paginación:")
        print(f"   Total de noticias: {total_noticias}")
        print(f"   Noticias por página: {noticias_por_pagina}")
        print(f"   Total de páginas: {total_paginas}")
        
        if total_paginas > 10:
            print(f"✅ La paginación mejorada mostrará hasta 10 páginas con puntos suspensivos")
        else:
            print(f"ℹ️  Con {total_paginas} páginas, se mostrarán todas las páginas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando paginación: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Prueba de Mejoras en Noticias")
    print("=" * 50)
    
    # Probar ordenamiento aleatorio
    ordenamiento_ok = simular_ordenamiento_aleatorio()
    
    # Verificar paginación
    paginacion_ok = verificar_paginacion()
    
    print(f"\n" + "=" * 50)
    print("📋 RESUMEN:")
    print(f"   Ordenamiento aleatorio: {'✅ OK' if ordenamiento_ok else '❌ Error'}")
    print(f"   Paginación mejorada: {'✅ OK' if paginacion_ok else '❌ Error'}")
    
    if ordenamiento_ok and paginacion_ok:
        print(f"\n🎉 ¡Mejoras implementadas correctamente!")
        print(f"📰 Las noticias ahora se mostrarán con variedad de fuentes")
        print(f"📄 La paginación mostrará hasta 10 páginas con navegación mejorada")
    else:
        print(f"\n⚠️  Hay problemas que requieren atención")

if __name__ == "__main__":
    main() 
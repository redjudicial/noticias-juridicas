#!/usr/bin/env python3
"""
Script para probar la extracción universal de fechas
"""

import requests
from bs4 import BeautifulSoup
from backend.scrapers.fuentes.date_extractor import date_extractor
from datetime import datetime

def test_fecha_especifica(url: str):
    """Probar extracción de fecha de una URL específica"""
    print(f"🔍 Probando extracción de fecha: {url}")
    print("-" * 60)
    
    try:
        # Obtener la página
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraer fecha usando el extractor universal
        fecha = date_extractor.extract_date_from_html(soup, url)
        
        if fecha:
            print(f"✅ FECHA EXTRAÍDA: {fecha}")
            print(f"📅 Formato legible: {fecha.strftime('%d de %B de %Y')}")
            print(f"🕐 Hora: {fecha.strftime('%H:%M:%S')}")
        else:
            print("❌ NO SE PUDO EXTRAER FECHA")
        
        # Mostrar fragmento del contenido donde podría estar la fecha
        contenido = soup.get_text()[:500]
        print(f"\n📄 Fragmento del contenido:")
        print(contenido)
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    # URLs de prueba con diferentes formatos de fecha
    urls_prueba = [
        "https://www.minjusticia.gob.cl/proyecto-de-ley-que-crea-el-servicio-nacional-de-acceso-a-la-justicia-y-la-defensoria-de-victimas-de-delitos-2/",
        "https://www.sii.cl/noticias/2025/310725noti01pcr.htm",
        "https://www.inapi.cl/sala-de-prensa/detalle-noticia/cuenta-publica-en-talca-inapi-destaca-avances-en-pi-y-anuncia-fortalecimiento-en-regiones"
    ]
    
    for url in urls_prueba:
        test_fecha_especifica(url)
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main() 
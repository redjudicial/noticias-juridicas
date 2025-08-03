#!/usr/bin/env python3
"""
Script para prevenir que el texto problemático del Tribunal Ambiental aparezca en futuras noticias
"""

import os
import sys
import re
from typing import Dict, List, Optional
from datetime import datetime, timezone

# Agregar el directorio al path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.scrapers.fuentes.base_scraper import BaseScraper

class PrevencionTextoProblematico:
    """Clase para prevenir texto problemático en noticias"""
    
    def __init__(self):
        # Patrones de texto problemático a detectar y eliminar
        self.patrones_problematicos = [
            # Patrones específicos del Tribunal Ambiental
            r'Acceder al expediente de la causa[A-Z0-9\-]+.*?contacto@tribunalambiental\.cl\.',
            r'Acceder al expediente[A-Z0-9\-]+.*?contacto@tribunalambiental\.cl\.',
            r'Morandé 360, Piso 8, Santiago.*?contacto@tribunalambiental\.cl\.',
            r'Piso 8, Santiago\([0-9\s\+]+\)contacto@tribunalambiental\.cl\.',
            r'\([0-9\s\+]+\)contacto@tribunalambiental\.cl\.',
            r'contacto@tribunalambiental\.cl\.',
            r'R-[0-9\-]+ Morandé 360, Piso 8, Santiago',
            r'Piso 8, Santiago\([0-9\s\+]+\), Piso 8, Santiago',
            
            # Patrones más generales de información de contacto
            r'Acceder al expediente.*?contacto@[a-zA-Z0-9\.\-]+\.[a-zA-Z]{2,}',
            r'Morandé 360.*?contacto@[a-zA-Z0-9\.\-]+\.[a-zA-Z]{2,}',
            r'Piso 8, Santiago.*?contacto@[a-zA-Z0-9\.\-]+\.[a-zA-Z]{2,}',
        ]
        
        # Texto de reemplazo para información de contacto
        self.texto_reemplazo = "Para más información, consulte la página oficial del tribunal."
    
    def limpiar_contenido(self, contenido: str, fuente: str = None) -> str:
        """Limpiar contenido de texto problemático"""
        if not contenido:
            return contenido
        
        contenido_limpio = contenido
        
        # Aplicar patrones específicos para tribunales ambientales
        if fuente and 'ambiental' in fuente.lower():
            for patron in self.patrones_problematicos:
                contenido_limpio = re.sub(patron, self.texto_reemplazo, contenido_limpio, flags=re.IGNORECASE | re.DOTALL)
        
        # Limpiar espacios múltiples
        contenido_limpio = re.sub(r'\s+', ' ', contenido_limpio)
        contenido_limpio = contenido_limpio.strip()
        
        return contenido_limpio
    
    def limpiar_titulo(self, titulo: str, fuente: str = None) -> str:
        """Limpiar título de texto problemático"""
        if not titulo:
            return titulo
        
        titulo_limpio = titulo
        
        # Aplicar patrones específicos para tribunales ambientales
        if fuente and 'ambiental' in fuente.lower():
            for patron in self.patrones_problematicos:
                titulo_limpio = re.sub(patron, '', titulo_limpio, flags=re.IGNORECASE)
        
        # Limpiar espacios múltiples
        titulo_limpio = re.sub(r'\s+', ' ', titulo_limpio)
        titulo_limpio = titulo_limpio.strip()
        
        return titulo_limpio
    
    def detectar_texto_problematico(self, texto: str) -> List[str]:
        """Detectar si hay texto problemático en el contenido"""
        problemas_encontrados = []
        
        for patron in self.patrones_problematicos:
            matches = re.findall(patron, texto, re.IGNORECASE | re.DOTALL)
            if matches:
                problemas_encontrados.append(f"Patrón: {patron}, Coincidencias: {len(matches)}")
        
        return problemas_encontrados
    
    def procesar_noticia(self, noticia: Dict) -> Dict:
        """Procesar una noticia completa para eliminar texto problemático"""
        fuente = noticia.get('fuente', '')
        
        # Limpiar título
        if 'titulo' in noticia:
            noticia['titulo'] = self.limpiar_titulo(noticia['titulo'], fuente)
        
        # Limpiar contenido
        if 'cuerpo_completo' in noticia:
            noticia['cuerpo_completo'] = self.limpiar_contenido(noticia['cuerpo_completo'], fuente)
        
        if 'contenido' in noticia:
            noticia['contenido'] = self.limpiar_contenido(noticia['contenido'], fuente)
        
        # Detectar problemas
        texto_completo = f"{noticia.get('titulo', '')} {noticia.get('cuerpo_completo', '')} {noticia.get('contenido', '')}"
        problemas = self.detectar_texto_problematico(texto_completo)
        
        if problemas:
            print(f"⚠️  Texto problemático detectado en noticia de {fuente}:")
            for problema in problemas:
                print(f"   - {problema}")
        
        return noticia

def crear_script_prevencion():
    """Crear un script que se puede integrar en los scrapers"""
    
    script_content = '''#!/usr/bin/env python3
"""
Módulo de prevención de texto problemático para scrapers
"""

import re
from typing import Dict

class PrevencionTextoProblematico:
    """Clase para prevenir texto problemático en noticias"""
    
    def __init__(self):
        # Patrones de texto problemático a detectar y eliminar
        self.patrones_problematicos = [
            # Patrones específicos del Tribunal Ambiental
            r'Acceder al expediente de la causa[A-Z0-9\-]+.*?contacto@tribunalambiental\.cl\.',
            r'Acceder al expediente[A-Z0-9\-]+.*?contacto@tribunalambiental\.cl\.',
            r'Morandé 360, Piso 8, Santiago.*?contacto@tribunalambiental\.cl\.',
            r'Piso 8, Santiago\\([0-9\\s\\+]+\\)contacto@tribunalambiental\\.cl\\.',
            r'\\([0-9\\s\\+]+\\)contacto@tribunalambiental\\.cl\\.',
            r'contacto@tribunalambiental\\.cl\\.',
            r'R-[0-9\\-]+ Morandé 360, Piso 8, Santiago',
            r'Piso 8, Santiago\\([0-9\\s\\+]+\\)\\, Piso 8, Santiago',
        ]
        
        # Texto de reemplazo para información de contacto
        self.texto_reemplazo = "Para más información, consulte la página oficial del tribunal."
    
    def limpiar_contenido(self, contenido: str, fuente: str = None) -> str:
        """Limpiar contenido de texto problemático"""
        if not contenido:
            return contenido
        
        contenido_limpio = contenido
        
        # Aplicar patrones específicos para tribunales ambientales
        if fuente and 'ambiental' in fuente.lower():
            for patron in self.patrones_problematicos:
                contenido_limpio = re.sub(patron, self.texto_reemplazo, contenido_limpio, flags=re.IGNORECASE | re.DOTALL)
        
        # Limpiar espacios múltiples
        contenido_limpio = re.sub(r'\\s+', ' ', contenido_limpio)
        contenido_limpio = contenido_limpio.strip()
        
        return contenido_limpio
    
    def limpiar_titulo(self, titulo: str, fuente: str = None) -> str:
        """Limpiar título de texto problemático"""
        if not titulo:
            return titulo
        
        titulo_limpio = titulo
        
        # Aplicar patrones específicos para tribunales ambientales
        if fuente and 'ambiental' in fuente.lower():
            for patron in self.patrones_problematicos:
                titulo_limpio = re.sub(patron, '', titulo_limpio, flags=re.IGNORECASE)
        
        # Limpiar espacios múltiples
        titulo_limpio = re.sub(r'\\s+', ' ', titulo_limpio)
        titulo_limpio = titulo_limpio.strip()
        
        return titulo_limpio

# Instancia global para usar en scrapers
prevencion_texto = PrevencionTextoProblematico()
'''
    
    # Guardar el script
    with open('backend/scrapers/fuentes/prevencion_texto_problematico.py', 'w') as f:
        f.write(script_content)
    
    print("✅ Script de prevención creado: backend/scrapers/fuentes/prevencion_texto_problematico.py")

def main():
    """Función principal"""
    print("🛡️ SISTEMA DE PREVENCIÓN DE TEXTO PROBLEMÁTICO")
    print("=" * 50)
    
    # Crear script de prevención
    crear_script_prevencion()
    
    # Crear instancia de prevención
    prevencion = PrevencionTextoProblematico()
    
    # Ejemplo de uso
    texto_ejemplo = """
    Esta es una noticia del Tribunal Ambiental que contiene texto problemático:
    Acceder al expediente de la causaR-498-2025 Morandé 360, Piso 8, Santiago(56) 2 2393 69 00, Piso 8, Santiago(56) 2 2393 69 00contacto@tribunalambiental.cl.
    """
    
    print("\n🧪 PRUEBA DE LIMPIEZA:")
    print("Texto original:")
    print(texto_ejemplo)
    
    texto_limpio = prevencion.limpiar_contenido(texto_ejemplo, 'tribunal_ambiental')
    print("\nTexto limpio:")
    print(texto_limpio)
    
    # Detectar problemas
    problemas = prevencion.detectar_texto_problematico(texto_ejemplo)
    if problemas:
        print(f"\n⚠️  Problemas detectados: {len(problemas)}")
        for problema in problemas:
            print(f"   - {problema}")
    
    print("\n✅ Sistema de prevención configurado correctamente")
    print("📋 Para usar en scrapers, importar: from .prevencion_texto_problematico import prevencion_texto")

if __name__ == "__main__":
    main() 
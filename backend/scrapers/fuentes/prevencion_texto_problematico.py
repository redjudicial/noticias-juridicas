#!/usr/bin/env python3
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
            r'Piso 8, Santiago\([0-9\s\+]+\)contacto@tribunalambiental\.cl\.',
            r'\([0-9\s\+]+\)contacto@tribunalambiental\.cl\.',
            r'contacto@tribunalambiental\.cl\.',
            r'R-[0-9\-]+ Morandé 360, Piso 8, Santiago',
            r'Piso 8, Santiago\([0-9\s\+]+\)\, Piso 8, Santiago',
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

# Instancia global para usar en scrapers
prevencion_texto = PrevencionTextoProblematico()

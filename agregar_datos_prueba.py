#!/usr/bin/env python3
"""
Script para agregar datos de prueba a la base de datos
"""

import os
import sys
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

def agregar_datos_prueba():
    """Agregar datos de prueba a la base de datos"""
    
    try:
        from backend.database.supabase_client import SupabaseClient
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Error: Faltan credenciales de Supabase")
            return False
        
        client = SupabaseClient(supabase_url, supabase_key)
        
        # Datos de prueba
        noticias_prueba = [
            {
                'titulo': 'Corte Suprema confirma sentencia en caso de corrupción municipal',
                'resumen_ejecutivo': 'La Corte Suprema confirmó la sentencia condenatoria contra ex funcionarios municipales por el delito de cohecho. El fallo establece jurisprudencia importante sobre responsabilidad penal en casos de corrupción pública.',
                'cuerpo_completo': 'La Corte Suprema, en fallo unánime, confirmó la sentencia condenatoria dictada por la Corte de Apelaciones de Santiago contra tres ex funcionarios municipales por el delito de cohecho. Los condenados recibieron penas de 3 a 5 años de presidio menor en su grado medio, más multas de 20 UTM. El caso involucraba la adjudicación irregular de contratos de mantenimiento de áreas verdes por un monto superior a los 50 millones de pesos. El tribunal estableció que la conducta de los funcionarios constituía un claro caso de corrupción que afectaba la confianza pública en las instituciones.',
                'fecha_publicacion': (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                'fuente': 'poder_judicial',
                'fuente_nombre_completo': 'Poder Judicial de Chile',
                'url_origen': 'https://www.pjud.cl/noticia-ejemplo-1',
                'categoria': 'fallos',
                'hash_contenido': 'hash_test_4'
            },
            {
                'titulo': 'Ministerio de Justicia presenta nueva política de transparencia judicial',
                'resumen_ejecutivo': 'El Ministerio de Justicia anunció una nueva política de transparencia que mejorará el acceso público a información judicial y estadísticas del sistema legal chileno.',
                'cuerpo_completo': 'El Ministerio de Justicia y Derechos Humanos presentó hoy una nueva política de transparencia judicial que busca mejorar significativamente el acceso público a información del sistema judicial. La iniciativa incluye la creación de un portal web centralizado que permitirá consultar estadísticas judiciales, información sobre causas y sentencias, y datos sobre el funcionamiento de los tribunales. La política también contempla la implementación de un sistema de alertas para informar sobre cambios en el estado de las causas y la publicación de informes trimestrales sobre la gestión judicial.',
                'fecha_publicacion': (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                'fuente': 'minjusticia',
                'fuente_nombre_completo': 'Ministerio de Justicia y Derechos Humanos',
                'url_origen': 'https://www.minjusticia.gob.cl/noticia-ejemplo-2',
                'categoria': 'institucional',
                'hash_contenido': 'hash_test_5'
            },
            {
                'titulo': 'Fiscalía Regional obtiene condena histórica en caso de lavado de activos',
                'resumen_ejecutivo': 'La Fiscalía Regional de Valparaíso logró una condena histórica en un caso de lavado de activos que involucraba a una red internacional de narcotráfico.',
                'cuerpo_completo': 'La Fiscalía Regional de Valparaíso, a través de su Unidad de Lavado de Activos y Delitos Económicos, obtuvo una condena histórica contra cinco personas por el delito de lavado de activos. El caso involucraba una red internacional de narcotráfico que operaba en la región y que había lavado más de 2.000 millones de pesos a través de empresas fachada y propiedades inmobiliarias. Los condenados recibieron penas de 5 a 15 años de presidio mayor, además de multas de 50 UTM. El fiscal regional destacó que esta condena marca un precedente importante en la lucha contra el crimen organizado.',
                'fecha_publicacion': (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                'fuente': 'fiscalia',
                'fuente_nombre_completo': 'Ministerio Público - Fiscalía de Chile',
                'url_origen': 'https://www.fiscaliadechile.cl/noticia-ejemplo-3',
                'categoria': 'penal',
                'hash_contenido': 'hash_test_6'
            },
            {
                'titulo': 'Tribunal Constitucional rechaza requerimiento sobre reforma tributaria',
                'resumen_ejecutivo': 'El Tribunal Constitucional rechazó por unanimidad un requerimiento que cuestionaba la constitucionalidad de varios artículos de la reforma tributaria recientemente aprobada.',
                'cuerpo_completo': 'El Tribunal Constitucional, en fallo unánime, rechazó el requerimiento presentado por un grupo de senadores que cuestionaba la constitucionalidad de varios artículos de la reforma tributaria. El tribunal consideró que las disposiciones impugnadas no vulneran la Constitución Política de la República y que el proceso legislativo se ajustó a los procedimientos constitucionales establecidos. La sentencia establece que las modificaciones tributarias son competencia del legislador y que no existe inconstitucionalidad en las normas cuestionadas.',
                'fecha_publicacion': (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
                'fuente': 'tribunal_constitucional',
                'fuente_nombre_completo': 'Tribunal Constitucional de Chile',
                'url_origen': 'https://www.tribunalconstitucional.cl/noticia-ejemplo-4',
                'categoria': 'constitucional',
                'hash_contenido': 'hash_test_7'
            },
            {
                'titulo': 'Defensoría Penal Pública presenta informe sobre acceso a la justicia',
                'resumen_ejecutivo': 'La Defensoría Penal Pública presentó su informe anual sobre acceso a la justicia, destacando las mejoras en la cobertura de defensa penal pública en regiones.',
                'cuerpo_completo': 'La Defensoría Penal Pública presentó hoy su informe anual sobre acceso a la justicia, documento que analiza la cobertura y calidad de la defensa penal pública en todo el país. El informe destaca que durante el año 2024 se logró una cobertura del 95% en todas las regiones del país, con especial énfasis en zonas rurales y de difícil acceso. También se reportó una mejora significativa en los tiempos de respuesta y en la calidad de la defensa proporcionada. El defensor nacional destacó que estos resultados reflejan el compromiso de la institución con garantizar el derecho a defensa de todas las personas.',
                'fecha_publicacion': (datetime.now(timezone.utc) - timedelta(hours=10)).isoformat(),
                'fuente': 'dpp',
                'fuente_nombre_completo': 'Defensoría Penal Pública',
                'url_origen': 'https://www.dpp.cl/noticia-ejemplo-5',
                'categoria': 'institucional',
                'hash_contenido': 'hash_test_8'
            },
            {
                'titulo': 'Contraloría General detecta irregularidades en contratos de salud',
                'resumen_ejecutivo': 'La Contraloría General de la República detectó graves irregularidades en la adjudicación de contratos de servicios de salud en tres regiones del país.',
                'cuerpo_completo': 'La Contraloría General de la República emitió un informe de auditoría que detectó graves irregularidades en la adjudicación de contratos de servicios de salud en las regiones de Antofagasta, Valparaíso y Biobío. El informe revela que se adjudicaron contratos por más de 15.000 millones de pesos sin cumplir con los procedimientos de licitación pública establecidos por la ley. La Contraloría determinó que estas irregularidades afectan la transparencia y eficiencia del gasto público, y recomendó la implementación de medidas correctivas inmediatas.',
                'fecha_publicacion': (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat(),
                'fuente': 'contraloria',
                'fuente_nombre_completo': 'Contraloría General de la República',
                'url_origen': 'https://www.contraloria.cl/noticia-ejemplo-6',
                'categoria': 'administrativo',
                'hash_contenido': 'hash_test_9'
            }
        ]
        
        print("📝 Agregando datos de prueba a la base de datos...")
        
        noticias_agregadas = 0
        
        for noticia in noticias_prueba:
            try:
                # Verificar si ya existe
                noticia_existente = client.get_noticia_by_hash(noticia['hash_contenido'])
                
                if noticia_existente:
                    print(f"⚠️  Noticia ya existe: {noticia['titulo'][:50]}...")
                    continue
                
                # Insertar noticia
                noticia_id = client.insert_noticia(noticia)
                
                if noticia_id:
                    print(f"✅ Agregada: {noticia['titulo'][:50]}...")
                    noticias_agregadas += 1
                else:
                    print(f"❌ Error agregando: {noticia['titulo'][:50]}...")
                    
            except Exception as e:
                print(f"❌ Error procesando noticia: {e}")
        
        print(f"\n📊 Resumen:")
        print(f"   ✅ Noticias agregadas: {noticias_agregadas}")
        print(f"   📰 Total en BD: {client.count_noticias()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    agregar_datos_prueba() 
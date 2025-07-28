#!/usr/bin/env python3
"""
Script simple para crear la tabla noticias_juridicas en Supabase
Usa requests directos para ejecutar SQL
"""

import os
import requests
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('APIS_Y_CREDENCIALES.env')

def crear_tabla_supabase():
    """Crear tabla usando SQL directo"""
    
    # Configuración
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("❌ Error: Faltan credenciales de Supabase")
        return False
    
    print(f"🚀 Conectando a Supabase: {SUPABASE_URL}")
    
    # Headers
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    # SQL para crear la tabla (versión simplificada)
    sql_commands = [
        # Tabla principal
        """
        CREATE TABLE IF NOT EXISTS noticias_juridicas (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            titulo TEXT NOT NULL,
            titulo_original TEXT,
            subtitulo TEXT,
            resumen_ejecutivo TEXT,
            cuerpo_completo TEXT,
            extracto_fuente TEXT,
            fecha_publicacion TIMESTAMP WITH TIME ZONE NOT NULL,
            fecha_actualizacion TIMESTAMP WITH TIME ZONE,
            fecha_scraping TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            fuente TEXT NOT NULL,
            fuente_nombre_completo TEXT,
            url_origen TEXT NOT NULL,
            url_imagen TEXT,
            categoria TEXT,
            subcategoria TEXT,
            etiquetas TEXT[],
            palabras_clave TEXT[],
            tipo_documento TEXT,
            jurisdiccion TEXT,
            tribunal_organismo TEXT,
            numero_causa TEXT,
            rol_causa TEXT,
            autor TEXT,
            autor_cargo TEXT,
            ubicacion TEXT,
            region TEXT,
            hash_contenido TEXT UNIQUE,
            version INTEGER DEFAULT 1,
            es_actualizacion BOOLEAN DEFAULT false,
            relevancia_juridica INTEGER DEFAULT 0,
            impacto_publico INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Tabla de resúmenes
        """
        CREATE TABLE IF NOT EXISTS resumenes_juridicos (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            noticia_id UUID REFERENCES noticias_juridicas(id) ON DELETE CASCADE,
            titulo_resumen TEXT NOT NULL,
            subtitulo_resumen TEXT,
            resumen_contenido TEXT NOT NULL,
            puntos_clave TEXT[],
            implicaciones_juridicas TEXT,
            jurisprudencia_relacionada TEXT[],
            normas_citadas TEXT[],
            tipo_resumen TEXT CHECK (tipo_resumen IN ('ejecutivo', 'técnico', 'público')),
            nivel_tecnico TEXT CHECK (nivel_tecnico IN ('básico', 'intermedio', 'avanzado')),
            modelo_ia TEXT,
            tokens_utilizados INTEGER,
            fecha_generacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            version INTEGER DEFAULT 1,
            es_ultima_version BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Tabla de fuentes
        """
        CREATE TABLE IF NOT EXISTS fuentes_noticias (
            id SERIAL PRIMARY KEY,
            nombre_corto TEXT UNIQUE NOT NULL,
            nombre_completo TEXT NOT NULL,
            url_base TEXT NOT NULL,
            tipo_fuente TEXT CHECK (tipo_fuente IN ('rss', 'scraper', 'api', 'manual')),
            url_noticias TEXT,
            url_rss TEXT,
            selectores_css JSONB,
            headers_http JSONB,
            activa BOOLEAN DEFAULT true,
            frecuencia_actualizacion INTEGER DEFAULT 900,
            ultima_actualizacion TIMESTAMP WITH TIME ZONE,
            proxima_actualizacion TIMESTAMP WITH TIME ZONE,
            total_noticias INTEGER DEFAULT 0,
            noticias_hoy INTEGER DEFAULT 0,
            errores_consecutivos INTEGER DEFAULT 0,
            descripcion TEXT,
            categoria_principal TEXT,
            region_cobertura TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Tabla de logs
        """
        CREATE TABLE IF NOT EXISTS logs_scraping (
            id SERIAL PRIMARY KEY,
            fuente_id INTEGER REFERENCES fuentes_noticias(id),
            fuente_nombre TEXT NOT NULL,
            estado TEXT NOT NULL CHECK (estado IN ('iniciado', 'en_proceso', 'completado', 'error', 'timeout')),
            tipo_operacion TEXT CHECK (tipo_operacion IN ('scraping', 'rss', 'resumen', 'embedding')),
            noticias_encontradas INTEGER DEFAULT 0,
            noticias_nuevas INTEGER DEFAULT 0,
            noticias_actualizadas INTEGER DEFAULT 0,
            noticias_duplicadas INTEGER DEFAULT 0,
            resumenes_generados INTEGER DEFAULT 0,
            duracion_segundos INTEGER,
            memoria_utilizada_mb INTEGER,
            requests_realizados INTEGER DEFAULT 0,
            errores TEXT[],
            warnings TEXT[],
            stack_trace TEXT,
            user_agent TEXT,
            ip_origen TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        
        # Índices
        """
        CREATE INDEX IF NOT EXISTS idx_noticias_fecha ON noticias_juridicas(fecha_publicacion DESC);
        CREATE INDEX IF NOT EXISTS idx_noticias_fuente ON noticias_juridicas(fuente);
        CREATE INDEX IF NOT EXISTS idx_noticias_categoria ON noticias_juridicas(categoria);
        CREATE INDEX IF NOT EXISTS idx_noticias_hash ON noticias_juridicas(hash_contenido);
        CREATE INDEX IF NOT EXISTS idx_noticias_tipo_documento ON noticias_juridicas(tipo_documento);
        CREATE INDEX IF NOT EXISTS idx_noticias_jurisdiccion ON noticias_juridicas(jurisdiccion);
        """,
        
        # Políticas RLS
        """
        ALTER TABLE noticias_juridicas ENABLE ROW LEVEL SECURITY;
        ALTER TABLE resumenes_juridicos ENABLE ROW LEVEL SECURITY;
        ALTER TABLE fuentes_noticias ENABLE ROW LEVEL SECURITY;
        ALTER TABLE logs_scraping ENABLE ROW LEVEL SECURITY;
        """,
        
        # Políticas de acceso
        """
        DROP POLICY IF EXISTS "Lectura pública noticias" ON noticias_juridicas;
        CREATE POLICY "Lectura pública noticias" ON noticias_juridicas FOR SELECT USING (true);
        
        DROP POLICY IF EXISTS "Lectura pública resúmenes" ON resumenes_juridicos;
        CREATE POLICY "Lectura pública resúmenes" ON resumenes_juridicos FOR SELECT USING (true);
        
        DROP POLICY IF EXISTS "Lectura pública fuentes" ON fuentes_noticias;
        CREATE POLICY "Lectura pública fuentes" ON fuentes_noticias FOR SELECT USING (true);
        
        DROP POLICY IF EXISTS "Inserción backend noticias" ON noticias_juridicas;
        CREATE POLICY "Inserción backend noticias" ON noticias_juridicas FOR INSERT WITH CHECK (true);
        
        DROP POLICY IF EXISTS "Inserción backend resúmenes" ON resumenes_juridicos;
        CREATE POLICY "Inserción backend resúmenes" ON resumenes_juridicos FOR INSERT WITH CHECK (true);
        
        DROP POLICY IF EXISTS "Inserción backend logs" ON logs_scraping;
        CREATE POLICY "Inserción backend logs" ON logs_scraping FOR INSERT WITH CHECK (true);
        
        DROP POLICY IF EXISTS "Actualización backend noticias" ON noticias_juridicas;
        CREATE POLICY "Actualización backend noticias" ON noticias_juridicas FOR UPDATE USING (true);
        
        DROP POLICY IF EXISTS "Actualización backend fuentes" ON fuentes_noticias;
        CREATE POLICY "Actualización backend fuentes" ON fuentes_noticias FOR UPDATE USING (true);
        """,
        
        # Datos iniciales
        """
        INSERT INTO fuentes_noticias (nombre_corto, nombre_completo, url_base, tipo_fuente, url_noticias, categoria_principal, descripcion) VALUES
        ('poder_judicial', 'Poder Judicial de Chile', 'https://www.pjud.cl', 'scraper', 'https://www.pjud.cl/prensa-y-comunicaciones/noticias', 'judicial', 'Noticias oficiales del Poder Judicial de Chile'),
        ('tribunal_constitucional', 'Tribunal Constitucional de Chile', 'https://www.tribunalconstitucional.cl', 'scraper', 'https://www.tribunalconstitucional.cl/prensa/noticias/', 'constitucional', 'Noticias y comunicados del Tribunal Constitucional'),
        ('minjusticia', 'Ministerio de Justicia y Derechos Humanos', 'https://www.minjusticia.gob.cl', 'rss', 'https://www.minjusticia.gob.cl/category/noticias/', 'ministerial', 'Noticias del Ministerio de Justicia'),
        ('fiscalia', 'Ministerio Público - Fiscalía de Chile', 'https://www.fiscaliadechile.cl', 'rss', 'https://www.fiscaliadechile.cl/Fiscalia/rss/noticias.xml', 'penal', 'Noticias de la Fiscalía Nacional y Regionales'),
        ('dpp', 'Defensoría Penal Pública', 'https://www.dpp.cl', 'scraper', 'https://www.dpp.cl/sala-de-prensa/noticias/', 'penal', 'Noticias de la Defensoría Penal Pública'),
        ('contraloria', 'Contraloría General de la República', 'https://www.contraloria.cl', 'rss', 'https://www.portalanticorrupcion.cl/rss/contraloria', 'administrativo', 'Comunicados de la Contraloría General'),
        ('cde', 'Consejo de Defensa del Estado', 'https://www.cde.gob.cl', 'rss', 'https://www.portalanticorrupcion.cl/rss/cde', 'estatal', 'Noticias del Consejo de Defensa del Estado'),
        ('diario_oficial', 'Diario Oficial de la República de Chile', 'https://www.diariooficial.interior.gob.cl', 'scraper', 'https://www.diariooficial.interior.gob.cl/edicionelectronica/', 'normativo', 'Publicaciones oficiales del Diario Oficial')
        ON CONFLICT (nombre_corto) DO NOTHING;
        """,
        
        # Datos de prueba
        """
        INSERT INTO noticias_juridicas (titulo, resumen_ejecutivo, fecha_publicacion, fuente, categoria, url_origen, hash_contenido) VALUES
        ('Corte Suprema confirma sentencia en caso emblemático', 'La Corte Suprema confirmó la sentencia del tribunal de primera instancia en un caso que ha generado gran interés público.', NOW(), 'poder_judicial', 'fallos', 'https://www.pjud.cl/noticia-ejemplo', 'hash_test_1'),
        ('Ministerio de Justicia anuncia nueva política de transparencia', 'El Ministerio de Justicia presentó una nueva política de transparencia que mejorará el acceso a la información pública.', NOW() - INTERVAL '1 hour', 'minjusticia', 'institucional', 'https://www.minjusticia.gob.cl/noticia-ejemplo', 'hash_test_2'),
        ('Fiscalía Regional obtiene condena en caso de corrupción', 'La Fiscalía Regional de Santiago logró una importante condena en un caso de corrupción que involucraba a funcionarios públicos.', NOW() - INTERVAL '2 hours', 'fiscalia', 'penal', 'https://www.fiscaliadechile.cl/noticia-ejemplo', 'hash_test_3')
        ON CONFLICT (hash_contenido) DO NOTHING;
        """
    ]
    
    print(f"📋 Ejecutando {len(sql_commands)} comandos SQL...")
    
    success_count = 0
    error_count = 0
    
    for i, command in enumerate(sql_commands, 1):
        try:
            print(f"⏳ Ejecutando comando {i}/{len(sql_commands)}...")
            
            # Usar la función exec_sql de Supabase
            response = requests.post(
                f'{SUPABASE_URL}/rest/v1/rpc/exec_sql',
                headers=headers,
                json={'sql': command.strip()},
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ Comando {i} ejecutado exitosamente")
                success_count += 1
            else:
                print(f"❌ Error en comando {i}: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                error_count += 1
                
        except Exception as e:
            print(f"❌ Error ejecutando comando {i}: {e}")
            error_count += 1
    
    print(f"\n📊 Resumen:")
    print(f"✅ Comandos exitosos: {success_count}")
    print(f"❌ Comandos con error: {error_count}")
    
    if error_count == 0:
        print("🎉 ¡Tabla creada exitosamente!")
        return True
    else:
        print("⚠️  Algunos comandos fallaron. Revisa los errores arriba.")
        return False

def test_connection():
    """Probar conexión a Supabase"""
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
    
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("❌ Error: Faltan credenciales de Supabase")
        return False
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}'
    }
    
    try:
        response = requests.get(f'{SUPABASE_URL}/rest/v1/', headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Conexión a Supabase exitosa")
            return True
        else:
            print(f"❌ Error de conexión: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Script de creación de tabla noticias_juridicas")
    print("=" * 50)
    
    # Probar conexión
    if not test_connection():
        print("❌ No se pudo conectar a Supabase. Verifica las credenciales.")
        exit(1)
    
    # Crear tabla
    if crear_tabla_supabase():
        print("\n✅ Proceso completado!")
        print("\n🔗 Puedes probar el frontend ahora:")
        print("   - Abre frontend/index.html en tu navegador")
        print("   - O usa frontend/noticias-widget.html para el widget")
    else:
        print("❌ Error creando la tabla")
        exit(1) 
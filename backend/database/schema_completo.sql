-- ========================================
-- SCHEMA COMPLETO PARA NOTICIAS JURÍDICAS
-- Base de datos semántica para Red Judicial
-- ========================================

-- Tabla principal de noticias jurídicas (datos completos)
CREATE TABLE IF NOT EXISTS noticias_juridicas (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Información básica
    titulo TEXT NOT NULL,
    titulo_original TEXT, -- Título exacto de la fuente
    subtitulo TEXT,
    
    -- Contenido completo
    resumen_ejecutivo TEXT, -- Resumen generado por IA
    cuerpo_completo TEXT, -- Contenido completo de la noticia
    extracto_fuente TEXT, -- Extracto original de la fuente
    
    -- Metadatos de publicación
    fecha_publicacion TIMESTAMP WITH TIME ZONE NOT NULL,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE,
    fecha_scraping TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Fuente y origen
    fuente TEXT NOT NULL,
    fuente_nombre_completo TEXT,
    url_origen TEXT NOT NULL,
    url_imagen TEXT,
    
    -- Clasificación
    categoria TEXT,
    subcategoria TEXT,
    etiquetas TEXT[],
    palabras_clave TEXT[],
    
    -- Información legal específica
    tipo_documento TEXT, -- 'fallo', 'norma', 'comunicado', 'evento', etc.
    jurisdiccion TEXT, -- 'penal', 'civil', 'administrativo', etc.
    tribunal_organismo TEXT,
    numero_causa TEXT,
    rol_causa TEXT,
    
    -- Metadatos adicionales
    autor TEXT,
    autor_cargo TEXT,
    ubicacion TEXT,
    region TEXT,
    
    -- Control de duplicados y versiones
    hash_contenido TEXT UNIQUE,
    hash_titulo TEXT,
    version INTEGER DEFAULT 1,
    es_actualizacion BOOLEAN DEFAULT false,
    
    -- Campos para base semántica
    embedding_vector VECTOR(1536), -- Para búsquedas semánticas
    relevancia_juridica INTEGER DEFAULT 0, -- 1-10
    impacto_publico INTEGER DEFAULT 0, -- 1-10
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de resúmenes jurídicos generados
CREATE TABLE IF NOT EXISTS resumenes_juridicos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    noticia_id UUID REFERENCES noticias_juridicas(id) ON DELETE CASCADE,
    
    -- Resumen estructurado
    titulo_resumen TEXT NOT NULL,
    subtitulo_resumen TEXT,
    resumen_contenido TEXT NOT NULL,
    
    -- Análisis jurídico
    puntos_clave TEXT[], -- Array de puntos clave
    implicaciones_juridicas TEXT,
    jurisprudencia_relacionada TEXT[],
    normas_citadas TEXT[],
    
    -- Clasificación del resumen
    tipo_resumen TEXT CHECK (tipo_resumen IN ('ejecutivo', 'técnico', 'público')),
    nivel_tecnico TEXT CHECK (nivel_tecnico IN ('básico', 'intermedio', 'avanzado')),
    
    -- Metadatos del resumen
    modelo_ia TEXT, -- 'gpt-4', 'claude-3', etc.
    tokens_utilizados INTEGER,
    fecha_generacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Control de versiones
    version INTEGER DEFAULT 1,
    es_ultima_version BOOLEAN DEFAULT true,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de fuentes de noticias
CREATE TABLE IF NOT EXISTS fuentes_noticias (
    id SERIAL PRIMARY KEY,
    nombre_corto TEXT UNIQUE NOT NULL,
    nombre_completo TEXT NOT NULL,
    url_base TEXT NOT NULL,
    tipo_fuente TEXT CHECK (tipo_fuente IN ('rss', 'scraper', 'api', 'manual')),
    
    -- Configuración de scraping
    url_noticias TEXT,
    url_rss TEXT,
    selectores_css JSONB, -- Para scraping
    headers_http JSONB,
    
    -- Estado y control
    activa BOOLEAN DEFAULT true,
    frecuencia_actualizacion INTEGER DEFAULT 900, -- segundos
    ultima_actualizacion TIMESTAMP WITH TIME ZONE,
    proxima_actualizacion TIMESTAMP WITH TIME ZONE,
    
    -- Estadísticas
    total_noticias INTEGER DEFAULT 0,
    noticias_hoy INTEGER DEFAULT 0,
    errores_consecutivos INTEGER DEFAULT 0,
    
    -- Metadatos
    descripcion TEXT,
    categoria_principal TEXT,
    region_cobertura TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de logs detallados
CREATE TABLE IF NOT EXISTS logs_scraping (
    id SERIAL PRIMARY KEY,
    fuente_id INTEGER REFERENCES fuentes_noticias(id),
    fuente_nombre TEXT NOT NULL,
    
    -- Estado del proceso
    estado TEXT NOT NULL CHECK (estado IN ('iniciado', 'en_proceso', 'completado', 'error', 'timeout')),
    tipo_operacion TEXT CHECK (tipo_operacion IN ('scraping', 'rss', 'resumen', 'embedding')),
    
    -- Resultados
    noticias_encontradas INTEGER DEFAULT 0,
    noticias_nuevas INTEGER DEFAULT 0,
    noticias_actualizadas INTEGER DEFAULT 0,
    noticias_duplicadas INTEGER DEFAULT 0,
    resumenes_generados INTEGER DEFAULT 0,
    
    -- Métricas de rendimiento
    duracion_segundos INTEGER,
    memoria_utilizada_mb INTEGER,
    requests_realizados INTEGER DEFAULT 0,
    
    -- Errores y warnings
    errores TEXT[],
    warnings TEXT[],
    stack_trace TEXT,
    
    -- Metadatos
    user_agent TEXT,
    ip_origen TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de embeddings para búsqueda semántica
CREATE TABLE IF NOT EXISTS embeddings_noticias (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    noticia_id UUID REFERENCES noticias_juridicas(id) ON DELETE CASCADE,
    
    -- Vectores de embedding
    embedding_titulo VECTOR(1536),
    embedding_resumen VECTOR(1536),
    embedding_contenido VECTOR(1536),
    embedding_combinado VECTOR(1536),
    
    -- Metadatos del embedding
    modelo_embedding TEXT NOT NULL, -- 'text-embedding-3-small', etc.
    fecha_generacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tokens_utilizados INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de categorías y etiquetas
CREATE TABLE IF NOT EXISTS categorias_juridicas (
    id SERIAL PRIMARY KEY,
    nombre TEXT UNIQUE NOT NULL,
    descripcion TEXT,
    categoria_padre_id INTEGER REFERENCES categorias_juridicas(id),
    nivel INTEGER DEFAULT 1,
    activa BOOLEAN DEFAULT true,
    
    -- Configuración semántica
    palabras_clave TEXT[],
    sinonimos TEXT[],
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de jurisprudencia relacionada
CREATE TABLE IF NOT EXISTS jurisprudencia_relacionada (
    id SERIAL PRIMARY KEY,
    noticia_id UUID REFERENCES noticias_juridicas(id) ON DELETE CASCADE,
    
    -- Información de la jurisprudencia
    rol_causa TEXT,
    tribunal TEXT,
    fecha_sentencia DATE,
    tipo_relacion TEXT CHECK (tipo_relacion IN ('cita', 'confirma', 'revoca', 'modifica', 'relacionada')),
    
    -- Metadatos
    relevancia INTEGER DEFAULT 0, -- 1-10
    comentario TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ========================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- ========================================

-- Índices principales
CREATE INDEX IF NOT EXISTS idx_noticias_fecha ON noticias_juridicas(fecha_publicacion DESC);
CREATE INDEX IF NOT EXISTS idx_noticias_fuente ON noticias_juridicas(fuente);
CREATE INDEX IF NOT EXISTS idx_noticias_categoria ON noticias_juridicas(categoria);
CREATE INDEX IF NOT EXISTS idx_noticias_hash ON noticias_juridicas(hash_contenido);
CREATE INDEX IF NOT EXISTS idx_noticias_tipo_documento ON noticias_juridicas(tipo_documento);
CREATE INDEX IF NOT EXISTS idx_noticias_jurisdiccion ON noticias_juridicas(jurisdiccion);

-- Índices para búsqueda semántica
CREATE INDEX IF NOT EXISTS idx_embeddings_noticia ON embeddings_noticias(noticia_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_fecha ON embeddings_noticias(fecha_generacion);

-- Índices para resúmenes
CREATE INDEX IF NOT EXISTS idx_resumenes_noticia ON resumenes_juridicos(noticia_id);
CREATE INDEX IF NOT EXISTS idx_resumenes_tipo ON resumenes_juridicos(tipo_resumen);
CREATE INDEX IF NOT EXISTS idx_resumenes_fecha ON resumenes_juridicos(fecha_generacion);

-- Índices para logs
CREATE INDEX IF NOT EXISTS idx_logs_fuente ON logs_scraping(fuente_id);
CREATE INDEX IF NOT EXISTS idx_logs_estado ON logs_scraping(estado);
CREATE INDEX IF NOT EXISTS idx_logs_fecha ON logs_scraping(created_at);

-- ========================================
-- FUNCIONES Y TRIGGERS
-- ========================================

-- Función para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Función para generar hash de contenido
CREATE OR REPLACE FUNCTION generate_content_hash(titulo TEXT, cuerpo TEXT, fecha TIMESTAMP)
RETURNS TEXT AS $$
BEGIN
    RETURN encode(sha256((titulo || cuerpo || fecha::text)::bytea), 'hex');
END;
$$ LANGUAGE plpgsql;

-- Función para calcular relevancia jurídica
CREATE OR REPLACE FUNCTION calculate_juridical_relevance(
    tipo_doc TEXT,
    jurisdiccion TEXT,
    tribunal TEXT,
    palabras_clave TEXT[]
) RETURNS INTEGER AS $$
DECLARE
    relevancia INTEGER := 5; -- Base neutral
BEGIN
    -- Ajustar por tipo de documento
    CASE tipo_doc
        WHEN 'fallo' THEN relevancia := relevancia + 3;
        WHEN 'norma' THEN relevancia := relevancia + 2;
        WHEN 'comunicado' THEN relevancia := relevancia + 1;
        ELSE relevancia := relevancia + 0;
    END CASE;
    
    -- Ajustar por jurisdicción
    CASE jurisdiccion
        WHEN 'penal' THEN relevancia := relevancia + 2;
        WHEN 'civil' THEN relevancia := relevancia + 1;
        WHEN 'administrativo' THEN relevancia := relevancia + 1;
        ELSE relevancia := relevancia + 0;
    END CASE;
    
    -- Ajustar por tribunal
    IF tribunal LIKE '%Suprema%' THEN
        relevancia := relevancia + 2;
    ELSIF tribunal LIKE '%Apelaciones%' THEN
        relevancia := relevancia + 1;
    END IF;
    
    -- Limitar a rango 1-10
    RETURN GREATEST(1, LEAST(10, relevancia));
END;
$$ LANGUAGE plpgsql;

-- Triggers
CREATE TRIGGER update_noticias_updated_at 
    BEFORE UPDATE ON noticias_juridicas 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fuentes_updated_at 
    BEFORE UPDATE ON fuentes_noticias 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- DATOS INICIALES
-- ========================================

-- Insertar fuentes predefinidas
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

-- Insertar categorías jurídicas principales
INSERT INTO categorias_juridicas (nombre, descripcion, nivel, palabras_clave) VALUES
('Derecho Penal', 'Materias relacionadas con el derecho penal y procesal penal', 1, ARRAY['penal', 'criminal', 'delito', 'proceso penal', 'fiscalía', 'defensoría']),
('Derecho Civil', 'Materias de derecho civil y comercial', 1, ARRAY['civil', 'comercial', 'contratos', 'propiedad', 'familia']),
('Derecho Administrativo', 'Materias de derecho administrativo y constitucional', 1, ARRAY['administrativo', 'constitucional', 'estado', 'gobierno', 'servicios públicos']),
('Derecho Laboral', 'Materias laborales y de seguridad social', 1, ARRAY['laboral', 'trabajo', 'empleo', 'seguridad social', 'previsional']),
('Derecho Tributario', 'Materias tributarias y fiscales', 1, ARRAY['tributario', 'impuestos', 'fiscal', 'tributos', 'SII']),
('Derecho de Familia', 'Materias de derecho de familia', 2, ARRAY['familia', 'matrimonio', 'divorcio', 'hijos', 'alimentos']),
('Derecho Comercial', 'Materias comerciales y empresariales', 2, ARRAY['comercial', 'empresa', 'sociedades', 'quiebra', 'insolvencia']),
('Derecho Procesal', 'Materias de derecho procesal', 2, ARRAY['procesal', 'proceso', 'procedimiento', 'tribunal', 'sentencia'])
ON CONFLICT (nombre) DO NOTHING;

-- ========================================
-- POLÍTICAS RLS (Row Level Security)
-- ========================================

-- Habilitar RLS en todas las tablas
ALTER TABLE noticias_juridicas ENABLE ROW LEVEL SECURITY;
ALTER TABLE resumenes_juridicos ENABLE ROW LEVEL SECURITY;
ALTER TABLE fuentes_noticias ENABLE ROW LEVEL SECURITY;
ALTER TABLE logs_scraping ENABLE ROW LEVEL SECURITY;
ALTER TABLE embeddings_noticias ENABLE ROW LEVEL SECURITY;
ALTER TABLE categorias_juridicas ENABLE ROW LEVEL SECURITY;
ALTER TABLE jurisprudencia_relacionada ENABLE ROW LEVEL SECURITY;

-- Políticas para lectura pública
CREATE POLICY "Lectura pública noticias" ON noticias_juridicas FOR SELECT USING (true);
CREATE POLICY "Lectura pública resúmenes" ON resumenes_juridicos FOR SELECT USING (true);
CREATE POLICY "Lectura pública fuentes" ON fuentes_noticias FOR SELECT USING (true);
CREATE POLICY "Lectura pública categorías" ON categorias_juridicas FOR SELECT USING (true);

-- Políticas para inserción desde backend
CREATE POLICY "Inserción backend noticias" ON noticias_juridicas FOR INSERT WITH CHECK (true);
CREATE POLICY "Inserción backend resúmenes" ON resumenes_juridicos FOR INSERT WITH CHECK (true);
CREATE POLICY "Inserción backend logs" ON logs_scraping FOR INSERT WITH CHECK (true);
CREATE POLICY "Inserción backend embeddings" ON embeddings_noticias FOR INSERT WITH CHECK (true);

-- Políticas para actualización desde backend
CREATE POLICY "Actualización backend noticias" ON noticias_juridicas FOR UPDATE USING (true);
CREATE POLICY "Actualización backend fuentes" ON fuentes_noticias FOR UPDATE USING (true); 
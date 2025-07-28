-- ========================================
-- SCHEMA COMPLETO PARA NOTICIAS JURÍDICAS
-- Copiar y pegar en el SQL Editor de Supabase
-- ========================================

-- Tabla principal de noticias jurídicas
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

-- Tabla de resúmenes jurídicos
CREATE TABLE IF NOT EXISTS noticias_resumenes_juridicos (
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

-- Tabla de fuentes de noticias
CREATE TABLE IF NOT EXISTS noticias_fuentes (
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

-- Tabla de logs de scraping
CREATE TABLE IF NOT EXISTS noticias_logs_scraping (
    id SERIAL PRIMARY KEY,
    fuente_id INTEGER REFERENCES noticias_fuentes(id),
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

-- Tabla de embeddings para búsqueda semántica
CREATE TABLE IF NOT EXISTS noticias_embeddings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    noticia_id UUID REFERENCES noticias_juridicas(id) ON DELETE CASCADE,
    embedding_titulo VECTOR(1536),
    embedding_resumen VECTOR(1536),
    embedding_contenido VECTOR(1536),
    embedding_combinado VECTOR(1536),
    modelo_embedding TEXT NOT NULL,
    fecha_generacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tokens_utilizados INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de categorías y etiquetas
CREATE TABLE IF NOT EXISTS noticias_categorias (
    id SERIAL PRIMARY KEY,
    nombre TEXT UNIQUE NOT NULL,
    descripcion TEXT,
    categoria_padre_id INTEGER REFERENCES noticias_categorias(id),
    nivel INTEGER DEFAULT 1,
    activa BOOLEAN DEFAULT true,
    palabras_clave TEXT[],
    sinonimos TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de jurisprudencia relacionada
CREATE TABLE IF NOT EXISTS noticias_jurisprudencia_relacionada (
    id SERIAL PRIMARY KEY,
    noticia_id UUID REFERENCES noticias_juridicas(id) ON DELETE CASCADE,
    rol_causa TEXT,
    tribunal TEXT,
    fecha_sentencia DATE,
    tipo_relacion TEXT CHECK (tipo_relacion IN ('cita', 'confirma', 'revoca', 'modifica', 'relacionada')),
    relevancia INTEGER DEFAULT 0,
    comentario TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_noticias_fecha ON noticias_juridicas(fecha_publicacion DESC);
CREATE INDEX IF NOT EXISTS idx_noticias_fuente ON noticias_juridicas(fuente);
CREATE INDEX IF NOT EXISTS idx_noticias_categoria ON noticias_juridicas(categoria);
CREATE INDEX IF NOT EXISTS idx_noticias_hash ON noticias_juridicas(hash_contenido);
CREATE INDEX IF NOT EXISTS idx_noticias_tipo_documento ON noticias_juridicas(tipo_documento);
CREATE INDEX IF NOT EXISTS idx_noticias_jurisdiccion ON noticias_juridicas(jurisdiccion);

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para actualizar updated_at
CREATE TRIGGER update_noticias_updated_at 
    BEFORE UPDATE ON noticias_juridicas 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fuentes_updated_at 
    BEFORE UPDATE ON noticias_fuentes 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Habilitar Row Level Security
ALTER TABLE noticias_juridicas ENABLE ROW LEVEL SECURITY;
ALTER TABLE noticias_resumenes_juridicos ENABLE ROW LEVEL SECURITY;
ALTER TABLE noticias_fuentes ENABLE ROW LEVEL SECURITY;
ALTER TABLE noticias_logs_scraping ENABLE ROW LEVEL SECURITY;
ALTER TABLE noticias_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE noticias_categorias ENABLE ROW LEVEL SECURITY;
ALTER TABLE noticias_jurisprudencia_relacionada ENABLE ROW LEVEL SECURITY;

-- Políticas de acceso público (solo lectura)
CREATE POLICY "Lectura pública noticias" ON noticias_juridicas FOR SELECT USING (true);
CREATE POLICY "Lectura pública resúmenes" ON noticias_resumenes_juridicos FOR SELECT USING (true);
CREATE POLICY "Lectura pública fuentes" ON noticias_fuentes FOR SELECT USING (true);
CREATE POLICY "Lectura pública categorías" ON noticias_categorias FOR SELECT USING (true);

-- Políticas para inserción desde backend
CREATE POLICY "Inserción backend noticias" ON noticias_juridicas FOR INSERT WITH CHECK (true);
CREATE POLICY "Inserción backend resúmenes" ON noticias_resumenes_juridicos FOR INSERT WITH CHECK (true);
CREATE POLICY "Inserción backend logs" ON noticias_logs_scraping FOR INSERT WITH CHECK (true);
CREATE POLICY "Inserción backend embeddings" ON noticias_embeddings FOR INSERT WITH CHECK (true);

-- Políticas para actualización desde backend
CREATE POLICY "Actualización backend noticias" ON noticias_juridicas FOR UPDATE USING (true);
CREATE POLICY "Actualización backend fuentes" ON noticias_fuentes FOR UPDATE USING (true);

-- Insertar fuentes predefinidas
INSERT INTO noticias_fuentes (nombre_corto, nombre_completo, url_base, tipo_fuente, url_noticias, categoria_principal, descripcion) VALUES
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
INSERT INTO noticias_categorias (nombre, descripcion, nivel, palabras_clave) VALUES
('Derecho Penal', 'Materias relacionadas con el derecho penal y procesal penal', 1, ARRAY['penal', 'criminal', 'delito', 'proceso penal', 'fiscalía', 'defensoría']),
('Derecho Civil', 'Materias de derecho civil y comercial', 1, ARRAY['civil', 'comercial', 'contratos', 'propiedad', 'familia']),
('Derecho Administrativo', 'Materias de derecho administrativo y constitucional', 1, ARRAY['administrativo', 'constitucional', 'estado', 'gobierno', 'servicios públicos']),
('Derecho Laboral', 'Materias laborales y de seguridad social', 1, ARRAY['laboral', 'trabajo', 'empleo', 'seguridad social', 'previsional']),
('Derecho Tributario', 'Materias tributarias y fiscales', 1, ARRAY['tributario', 'impuestos', 'fiscal', 'tributos', 'SII']),
('Derecho de Familia', 'Materias de derecho de familia', 2, ARRAY['familia', 'matrimonio', 'divorcio', 'hijos', 'alimentos']),
('Derecho Comercial', 'Materias comerciales y empresariales', 2, ARRAY['comercial', 'empresa', 'sociedades', 'quiebra', 'insolvencia']),
('Derecho Procesal', 'Materias de derecho procesal', 2, ARRAY['procesal', 'proceso', 'procedimiento', 'tribunal', 'sentencia'])
ON CONFLICT (nombre) DO NOTHING;

-- Insertar datos de prueba
INSERT INTO noticias_juridicas (titulo, resumen_ejecutivo, fecha_publicacion, fuente, categoria, url_origen, hash_contenido) VALUES
('Corte Suprema confirma sentencia en caso emblemático', 'La Corte Suprema confirmó la sentencia del tribunal de primera instancia en un caso que ha generado gran interés público.', NOW(), 'poder_judicial', 'fallos', 'https://www.pjud.cl/noticia-ejemplo', 'hash_test_1'),
('Ministerio de Justicia anuncia nueva política de transparencia', 'El Ministerio de Justicia presentó una nueva política de transparencia que mejorará el acceso a la información pública.', NOW() - INTERVAL '1 hour', 'minjusticia', 'institucional', 'https://www.minjusticia.gob.cl/noticia-ejemplo', 'hash_test_2'),
('Fiscalía Regional obtiene condena en caso de corrupción', 'La Fiscalía Regional de Santiago logró una importante condena en un caso de corrupción que involucraba a funcionarios públicos.', NOW() - INTERVAL '2 hours', 'fiscalia', 'penal', 'https://www.fiscaliadechile.cl/noticia-ejemplo', 'hash_test_3')
ON CONFLICT (hash_contenido) DO NOTHING; 
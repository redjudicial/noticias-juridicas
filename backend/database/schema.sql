-- Tabla principal de noticias jurídicas
CREATE TABLE IF NOT EXISTS noticias_juridicas (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    titulo TEXT NOT NULL,
    resumen TEXT,
    cuerpo TEXT,
    fecha_publicacion TIMESTAMP WITH TIME ZONE NOT NULL,
    fuente TEXT NOT NULL,
    link_origen TEXT,
    categoria TEXT,
    etiquetas TEXT[],
    autor TEXT,
    imagen_url TEXT,
    hash_contenido TEXT UNIQUE, -- Para evitar duplicados
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_noticias_fecha ON noticias_juridicas(fecha_publicacion DESC);
CREATE INDEX IF NOT EXISTS idx_noticias_fuente ON noticias_juridicas(fuente);
CREATE INDEX IF NOT EXISTS idx_noticias_categoria ON noticias_juridicas(categoria);
CREATE INDEX IF NOT EXISTS idx_noticias_hash ON noticias_juridicas(hash_contenido);

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para actualizar updated_at
DROP TRIGGER IF EXISTS update_noticias_updated_at ON noticias_juridicas;
CREATE TRIGGER update_noticias_updated_at 
    BEFORE UPDATE ON noticias_juridicas 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Tabla de fuentes para normalización
CREATE TABLE IF NOT EXISTS fuentes_noticias (
    id SERIAL PRIMARY KEY,
    nombre TEXT UNIQUE NOT NULL,
    url_base TEXT,
    tipo_fuente TEXT CHECK (tipo_fuente IN ('rss', 'scraper', 'api')),
    activa BOOLEAN DEFAULT true,
    ultima_actualizacion TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insertar fuentes predefinidas
INSERT INTO fuentes_noticias (nombre, url_base, tipo_fuente) VALUES
('poder_judicial', 'https://www.pjud.cl', 'scraper'),
('tribunal_constitucional', 'https://www.tribunalconstitucional.cl', 'scraper'),
('minjusticia', 'https://www.minjusticia.gob.cl', 'rss'),
('fiscalia', 'https://www.fiscaliadechile.cl', 'rss'),
('dpp', 'https://www.dpp.cl', 'scraper'),
('contraloria', 'https://www.contraloria.cl', 'rss'),
('cde', 'https://www.cde.gob.cl', 'rss'),
('diario_oficial', 'https://www.diariooficial.interior.gob.cl', 'scraper')
ON CONFLICT (nombre) DO NOTHING;

-- Tabla de logs para monitoreo
CREATE TABLE IF NOT EXISTS logs_scraping (
    id SERIAL PRIMARY KEY,
    fuente TEXT NOT NULL,
    estado TEXT NOT NULL,
    noticias_nuevas INTEGER DEFAULT 0,
    noticias_duplicadas INTEGER DEFAULT 0,
    errores TEXT,
    duracion_segundos INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Políticas RLS (Row Level Security)
ALTER TABLE noticias_juridicas ENABLE ROW LEVEL SECURITY;
ALTER TABLE fuentes_noticias ENABLE ROW LEVEL SECURITY;
ALTER TABLE logs_scraping ENABLE ROW LEVEL SECURITY;

-- Política para lectura pública de noticias
DROP POLICY IF EXISTS "Permitir lectura pública de noticias" ON noticias_juridicas;
CREATE POLICY "Permitir lectura pública de noticias" ON noticias_juridicas
    FOR SELECT USING (true);

-- Política para lectura de fuentes
DROP POLICY IF EXISTS "Permitir lectura de fuentes" ON fuentes_noticias;
CREATE POLICY "Permitir lectura de fuentes" ON fuentes_noticias
    FOR SELECT USING (true);

-- Política para logs (solo inserción desde el backend)
DROP POLICY IF EXISTS "Permitir inserción de logs" ON logs_scraping;
CREATE POLICY "Permitir inserción de logs" ON logs_scraping
    FOR INSERT WITH CHECK (true);

-- Insertar datos de prueba
INSERT INTO noticias_juridicas (titulo, resumen, fecha_publicacion, fuente, categoria, link_origen, hash_contenido) VALUES
('Corte Suprema confirma sentencia en caso emblemático', 'La Corte Suprema confirmó la sentencia del tribunal de primera instancia en un caso que ha generado gran interés público.', NOW(), 'poder_judicial', 'fallos', 'https://www.pjud.cl/noticia-ejemplo', 'hash1'),
('Ministerio de Justicia anuncia nueva política de transparencia', 'El Ministerio de Justicia presentó una nueva política de transparencia que mejorará el acceso a la información pública.', NOW() - INTERVAL '1 hour', 'minjusticia', 'institucional', 'https://www.minjusticia.gob.cl/noticia-ejemplo', 'hash2'),
('Fiscalía Regional obtiene condena en caso de corrupción', 'La Fiscalía Regional de Santiago logró una importante condena en un caso de corrupción que involucraba a funcionarios públicos.', NOW() - INTERVAL '2 hours', 'fiscalia', 'penal', 'https://www.fiscaliadechile.cl/noticia-ejemplo', 'hash3')
ON CONFLICT (hash_contenido) DO NOTHING; 
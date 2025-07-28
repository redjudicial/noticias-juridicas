-- Eliminar restricción única del hash_contenido
-- Ejecutar en Supabase SQL Editor

-- Eliminar la restricción única
ALTER TABLE noticias_juridicas DROP CONSTRAINT IF EXISTS noticias_juridicas_hash_contenido_key;

-- Agregar restricción única a url_origen en su lugar
ALTER TABLE noticias_juridicas ADD CONSTRAINT noticias_juridicas_url_origen_key UNIQUE (url_origen);

-- Crear índice en hash_contenido (sin restricción única)
CREATE INDEX IF NOT EXISTS idx_noticias_hash_contenido ON noticias_juridicas(hash_contenido);

-- Crear índice en url_origen
CREATE INDEX IF NOT EXISTS idx_noticias_url_origen ON noticias_juridicas(url_origen); 
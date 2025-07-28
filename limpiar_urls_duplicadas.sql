-- Limpiar URLs duplicadas antes de agregar restricción única
-- Ejecutar en Supabase SQL Editor

-- 1. Ver URLs duplicadas
SELECT url_origen, COUNT(*) as cantidad
FROM noticias_juridicas 
GROUP BY url_origen 
HAVING COUNT(*) > 1
ORDER BY cantidad DESC;

-- 2. Eliminar duplicados manteniendo la noticia más reciente
DELETE FROM noticias_juridicas 
WHERE id NOT IN (
    SELECT DISTINCT ON (url_origen) id
    FROM noticias_juridicas
    ORDER BY url_origen, fecha_publicacion DESC
);

-- 3. Verificar que no hay duplicados
SELECT url_origen, COUNT(*) as cantidad
FROM noticias_juridicas 
GROUP BY url_origen 
HAVING COUNT(*) > 1;

-- 4. Ahora agregar la restricción única
ALTER TABLE noticias_juridicas ADD CONSTRAINT noticias_juridicas_url_origen_key UNIQUE (url_origen);

-- 5. Crear índices
CREATE INDEX IF NOT EXISTS idx_noticias_hash_contenido ON noticias_juridicas(hash_contenido);
CREATE INDEX IF NOT EXISTS idx_noticias_url_origen ON noticias_juridicas(url_origen); 
-- @block distritos
SELECT nombre
FROM distritos
ORDER BY nombre;
-- @block distritos judiciales
SELECT nombre
FROM distritos
WHERE es_distrito_judicial = TRUE
ORDER BY nombre;
-- @block distritos whatsapp
SELECT id, nombre_corto
FROM distritos
WHERE nombre LIKE 'Distrito%';

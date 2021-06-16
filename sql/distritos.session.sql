-- @block distritos
SELECT nombre
FROM distritos
ORDER BY nombre;
-- @block distritos judiciales
SELECT nombre
FROM distritos
WHERE es_distrito_judicial = TRUE
ORDER BY nombre

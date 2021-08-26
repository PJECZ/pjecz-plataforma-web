-- @block distritos
SELECT nombre
FROM distritos
WHERE estatus = "A"
ORDER BY nombre;
-- @block distritos judiciales
SELECT nombre
FROM distritos
WHERE es_distrito_judicial = TRUE AND estatus = "A"
ORDER BY nombre;
-- @block solo distritos
SELECT nombre_corto
FROM distritos
WHERE nombre LIKE 'Distrito%' AND estatus = "A"
ORDER BY nombre_corto;

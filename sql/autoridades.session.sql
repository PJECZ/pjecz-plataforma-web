-- @block jurisdiccionales activas
SELECT autoridades.clave,
    distritos.nombre,
    autoridades.descripcion
FROM autoridades
    INNER JOIN distritos ON autoridades.distrito = distritos.id
WHERE autoridades.es_jurisdiccional = TRUE
    AND autoridades.estatus = 'A'
ORDER BY autoridades.clave;
-- @block jurisdiccionales inactivas
SELECT autoridades.clave,
    distritos.nombre,
    autoridades.descripcion
FROM autoridades
    INNER JOIN distritos ON autoridades.distrito = distritos.id
WHERE autoridades.es_jurisdiccional = TRUE
    AND autoridades.estatus = 'B'
ORDER BY autoridades.clave;
-- @block no jusrisdiccionales activas
SELECT autoridades.clave,
    distritos.nombre,
    autoridades.descripcion
FROM autoridades
    INNER JOIN distritos ON autoridades.distrito = distritos.id
WHERE autoridades.es_jurisdiccional = FALSE
    AND autoridades.estatus = 'A'
ORDER BY autoridades.clave;
-- @block no jusrisdiccionales inactivas
SELECT autoridades.clave,
    distritos.nombre,
    autoridades.descripcion
FROM autoridades
    INNER JOIN distritos ON autoridades.distrito = distritos.id
WHERE autoridades.es_jurisdiccional = FALSE
    AND autoridades.estatus = 'B'
ORDER BY autoridades.clave;

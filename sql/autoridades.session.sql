-- @block autoridades jurisdiccionales activas
SELECT autoridades.clave,
    distritos.nombre AS distrito,
    autoridades.descripcion
FROM autoridades
    INNER JOIN distritos ON autoridades.distrito_id = distritos.id
WHERE autoridades.es_jurisdiccional = TRUE
    AND autoridades.estatus = 'A'
ORDER BY autoridades.clave;
-- @block autoridades jurisdiccionales inactivas
SELECT autoridades.clave,
    distritos.nombre AS distrito,
    autoridades.descripcion
FROM autoridades
    INNER JOIN distritos ON autoridades.distrito_id = distritos.id
WHERE autoridades.es_jurisdiccional = TRUE
    AND autoridades.estatus = 'B'
ORDER BY autoridades.clave;
-- @block autoridades no jusrisdiccionales activas
SELECT autoridades.clave,
    distritos.nombre AS distrito,
    autoridades.descripcion
FROM autoridades
    INNER JOIN distritos ON autoridades.distrito_id = distritos.id
WHERE autoridades.es_jurisdiccional = FALSE
    AND autoridades.estatus = 'A'
ORDER BY autoridades.clave;
-- @block autoridades no jusrisdiccionales inactivas
SELECT autoridades.clave,
    distritos.nombre AS distrito,
    autoridades.descripcion
FROM autoridades
    INNER JOIN distritos ON autoridades.distrito_id = distritos.id
WHERE autoridades.es_jurisdiccional = FALSE
    AND autoridades.estatus = 'B'
ORDER BY autoridades.clave;
-- @block organos_jurisdiccionales y autoridades
SELECT autoridades.organo_jurisdiccional,
    autoridades.clave,
    autoridades.descripcion
FROM autoridades
WHERE autoridades.estatus = 'A'
    AND autoridades.es_jurisdiccional = TRUE
    AND autoridades.es_notaria = FALSE
ORDER BY organo_jurisdiccional,
    clave;
-- @block updates
UPDATE autoridades
SET organo_jurisdiccional = 'NO DEFINIDO';
UPDATE autoridades
SET materia_id = 1;
-- @block organos_jurisdiccionales, materias y autoridades
SELECT autoridades.organo_jurisdiccional,
    materias.nombre AS materia,
    autoridades.clave,
    autoridades.descripcion
FROM autoridades
    INNER JOIN materias ON autoridades.materia_id = materias.id
WHERE autoridades.estatus = 'A'
    AND autoridades.es_jurisdiccional = TRUE
    AND autoridades.es_notaria = FALSE
ORDER BY organo_jurisdiccional,
    materia,
    clave

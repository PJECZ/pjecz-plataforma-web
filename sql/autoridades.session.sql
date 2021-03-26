-- @block autoridades
-- @conn pjecz_plataforma_web
SELECT distritos.nombre,
    autoridades.descripcion,
    autoridades.clave,
    autoridades.es_jurisdiccional,
    autoridades.estatus
FROM autoridades
    INNER JOIN distritos ON autoridades.distrito = distritos.id
ORDER BY autoridades.clave;

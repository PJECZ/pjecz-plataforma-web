-- @block materias
SELECT nombre
FROM materias
WHERE estatus = "A"
ORDER BY nombre ASC;
-- @block tipos de juicios
SELECT materias.nombre,
    materias_tipos_juicios.descripcion
FROM materias,
    materias_tipos_juicios
WHERE materias_tipos_juicios.materia_id = materias.id
    AND materias.estatus = "A"
    AND materias_tipos_juicios.estatus = "A"
ORDER BY materias.nombre,
    materias_tipos_juicios.descripcion;

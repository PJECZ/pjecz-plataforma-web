SELECT d.nombre AS distrito,
    a.descripcion AS autoridad,
    la.fecha,
    la.descripcion,
    la.url
FROM listas_de_acuerdos AS la,
    autoridades AS a,
    distritos AS d
WHERE la.autoridad = a.id
    AND a.distrito = d.id
ORDER BY la.fecha DESC
LIMIT 100;

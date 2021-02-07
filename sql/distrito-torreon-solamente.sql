-- @block dar todas las autoridades y distritos de alta
UPDATE autoridades
SET estatus = 'A';
UPDATE distritos
SET estatus = 'A';
-- @block dar de baja distritos todos menos Torreón
UPDATE distritos
SET estatus = 'B'
WHERE nombre != 'Distrito de Torreón';
SELECT nombre
FROM distritos
WHERE estatus = 'A';
-- @block dar de baja autoridades con distritos dados de baja
UPDATE autoridades
SET estatus = 'B'
WHERE distrito IN (
        SELECT id
        FROM distritos
        WHERE estatus = 'B'
    );
SELECT d.nombre,
    a.descripcion,
    a.directorio_listas_de_acuerdos
FROM autoridades AS a,
    distritos AS d
WHERE a.estatus = 'A'
    AND a.distrito = d.id;

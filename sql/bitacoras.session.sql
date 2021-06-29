--@block Contar por modulo
SELECT modulo, count(*)
FROM bitacoras
WHERE creado >= '2021-06-15'
GROUP BY modulo;

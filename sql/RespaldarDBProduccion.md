# Respaldar base de datos en produccion

Pasos a seguir

1. Ingrese a Diana con `ssh pjecz-plataforma-web@diana`
2. Cambiese al directorio `cd ~/Descargas/Minerva/pjecz_plataforma_web`
3. Haga el respaldo `pg_dump -F t pjecz_plataforma_web > pjecz_plataforma_web-2022-MM-DD-HHMM.tar`
4. Comprima el archivo TAR con `gzip pjecz_plataforma_web-2022-MM-DD-HHMM.tar`
5. Copie a su equipo ese archivo tar.gz
6. Descomprima con `gunzip pjecz_plataforma_web-2022-MM-DD-HHMM.tar.gz`
7. Para restablecer en su equipo local, elimine y ejecute pg_restore

## Paso 3: Haga el respaldo

Comando

    pg_dump -F t pjecz_plataforma_web > pjecz_plataforma_web-2022-MM-DD-HHMM.tar

Parametros

- Salida a un solo archivo TAR con `-F t`
- Nombre de la base de datos `pjecz_plataforma_web`
- Salida a un archivo con YYYY-MM-DD-HHMM

## Paso 7: Reestablecer

Primero eliminar las tablas y registros con el alias programado

    eliminar-tablas-pjecz-plataforma-web

Comando

    pg_restore -F t -d pjecz_plataforma_web ~/Downloads/Minerva/pjecz_plataforma_web/pjecz_plataforma_web-2022-02-23-1242.tar

Parametros

- El orgen es un TAR con `-F t`
- Nombre de la base de datos `-d pjecz_plataforma_web`
- Ruta al archivo TAR

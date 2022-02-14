# Como actualizar la base de datos en produccion

Modificar la base de datos en produccion requiere

1. Localmente eliminar las tablas y ejecutar `plataforma_web db inicializar`
2. Usar un contenedor PgAdmin4 para copiar-pegar los comandos SQL
3. Escribir un archivo SQL con todas las instrucciones para crear o modificar
4. Haga un respaldo de la base de datos en produccion, copie y descomprima
5. Eliminar las tablas y restaurar una copia de la base de datos de produccion
6. Ejecutar ese archivo SQL para asegurarse que hara bien su trabajo en produccion
7. Copiar ese archivo SQL a VM Diana y ejecutarlo en produccion

## Paso 1: Eliminar las tablas

Lo mas practico es crear un archivo SQL en `~/.bashrc.d/eliminar-y-crear-pjecz-plataforma-web.sql`

    DROP SCHEMA IF EXISTS public CASCADE;
    CREATE SCHEMA public;
    GRANT ALL ON SCHEMA public TO public;
    GRANT ALL ON SCHEMA public TO adminpjeczplataformaweb;

Y agregar estos aliases a `~/.bashrc.d/61-postgresql.sql`

    alias eliminar-y-crear-pjecz-plataforma-web="psql -f ~/.bashrc.d/eliminar-y-crear-pjecz-plataforma-web.sql pjecz_plataforma_web"
    echo "-- PostgreSQL eliminar tablas"
    echo "   eliminar-y-crear-pjecz-plataforma-web"
    echo

Asi puede ejecutar con su usuario con cuenta en postgresql de altos privilegios

    eliminar-y-crear-pjecz-plataforma-web

## Paso 2: Usar un contenedor PgAdmin4 para copiar-pegar los comandos SQL

Este comando levanta un contenedor PgAdmin4 que puede comunicarse al servidor local

    podman run --rm \
        --env-file .env \
        --name pgadmin4 \
        -p 8086:80 \
        --network slirp4netns:allow_host_loopback=true \
        dpage/pgadmin4:latest

Mantenga corriendo este contenedor en su propia terminal. Con CTRL-C se termina.

Ingrese en su navegador de internet

    http://127.0.0.1:8086

Configure PgAdmin4 para que se conecte a 10.0.2.2 con su usuario con roles mayores

## Paso 3: Escribir un archivo SQL con todas las instrucciones para crear o modificar

Escriba los comandos SQL para crear o modificar la base de datos, por ejemplo en `sql/2022-XX-XX-descripcion.sql`

Copie las ordenes CREATE de las tablas y las secuencias.

Pegue y defina el orden correcto

## Paso 4: Haga un respaldo de la base de datos en produccion, copie y descomprima

Copiar archivo comprimido desde Diana y descomprimir

    cd ~/Downloads/Minerva/pjecz_plataforma_web
    gunzip pjecz_plataforma_web-202X-XX-XX-XXXX.tar.gz

## Paso 5: Eliminar las tablas y restaurar una copia de la base de datos de produccion

Eliminar

    eliminar-y-crear-pjecz-plataforma-web

Restaurar

    pg_restore -F t -d pjecz_plataforma_web ~/Downloads/Minerva/pjecz_plataforma_web/pjecz_plataforma_web-2022-02-10-0845.tar

## Paso 6

Probar los cambios

    psql -d pjecz_plataforma_web -f ~/Documents/GitHub/su_usuario/pjecz_plataforma_web/sql/2022-02-10-soportes.sql

Regrese al paso 3 en caso de fallar

## Restaurar

Restaurar

    pg_restore -F t -d pjecz_plataforma_web pjecz_plataforma_web-202X-XX-XX-XXXX.tar

## Reiniciar

Ingresar al entorno virtual de pjecz-plataforma-web y ejecutar

    plataforma_web db reiniciar

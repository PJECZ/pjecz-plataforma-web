# PgAdmin4

Debe de tener un archivo `.env` donde escribira los parametros para el contenedor

    PGADMIN_DEFAULT_EMAIL=guillermo.valdes@pjecz.gob.mx
    PGADMIN_DEFAULT_PASSWORD=********

Cambie al directorio donde esta ese archivo `.env`

Ejecute este comando que levanta un contenedor PgAdmin4 que puede comunicarse al servidor local

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

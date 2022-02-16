# PostgreSQL

## Instalar en Fedora

Instalar cliente y servidor

    sudo dnf install postgresql postgresql-server postgis postgis-client

Inicializar cluster

    sudo postgresql-setup --initdb --unit postgresql

Arrancar daemon

    sudo systemctl start postgresql

Que al encender arranque

    sudo systemctl enable postgresql

Listar tablas

    sudo -u postgres psql -l

## Usuario con todos los privilegios

Conviene crear una cuenta en postgres igual que su usuario con todos los privilegios

    sudo su - postgres
    createuser --createdb --createrole --superuser su_usuario
    exit

Crear un archivo `~/.bashrc.d/61-postgresql.sh` para cargar variables de entorno

    export PGHOST=127.0.0.1
    export PGPORT=5432
    export PGUSER=su_usuario
    export PGPASSWORD=new_password

Cierre y abra la terminal para que este cambio sea efectivo

Pruebe ver esas variables

    echo $PGUSER

Edite `pg_hba.conf` con el usuario postgres

    sudo su - postgres
    nano ~/data/pg_hba.conf

Agregue su usuario, escriba la linea antes de `host all all`

    # IPv4 local connections:
    host    all             su_usuario      127.0.0.1/32            md5
    host    all             all             127.0.0.1/32            ident

Salga del usuario postgres y reinicie el daemon

    exit
    sudo systemctl restart postgresql

Defina la contrasena

    sudo su - postgres
    psql -d template1 -c "ALTER USER su_usuario WITH PASSWORD 'new_password';"
    exit

Pruebe

    psql -l

## Usuarios y bases de datos para cada sistema

Para cada sistema cree su propio usuario y contrasena

    createuser --pwprompt adminpjeczplataformaweb

Por defecto no se pueden crear bases de datos, usuarios o ser superusuario

Crear las bases de datos y hacer duenos a los usuarios

    createdb --owner adminpjeczplataformaweb pjecz_plataforma_web

Edite pg_hba.conf con el usuario postgres

    sudo su - postgres
    nano ~/data/pg_hba.conf

Agregue

    # IPv4 local connections:
    host    all                   su_usuario               127.0.0.1/32  md5
    host    pjecz_plataforma_web  adminpjeczplataformaweb  127.0.0.1/32  md5
    host    all                   all                      127.0.0.1/32  ident

Salga del usuario postgres y reinicie el daemon

    exit
    sudo systemctl restart postgresql

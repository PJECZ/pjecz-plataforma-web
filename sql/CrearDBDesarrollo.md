# Crear base de datos para desarrollo

Crear el usuario y contrasena para este sistema en PostgreSQL

    createuser --pwprompt adminpjeczplataformaweb

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

Salga del usuario postgres y reinicie el servicio

    exit
    sudo systemctl restart postgresql

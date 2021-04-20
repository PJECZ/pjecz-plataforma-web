# pjecz-plataforma-web

Administrador de contenidos del sitio web del PJECZ.

## Crear Entorno Virtual

Crear el enorno virtual dentro de la copia local del repositorio, con

    python -m venv venv

O con virtualenv

    virtualenv -p python3 venv

Active el entorno virtual, en Linux con...

    source venv/bin/activate

O en windows con

    venv/Scripts/activate

Verifique que haya el mínimo de paquetes con

    pip list

Actualice el pip de ser necesario

    pip install --upgrade pip

Y luego instale los paquetes que requiere Plataforma Web

    pip install -r requirements.txt

Verifique con

    pip list

## Configurar

Crear archivo .env con las variables de entorno, por ejemplo:

    FLASK_APP=plataforma_web.app
    FLASK_DEBUG=1
    SECRET_KEY=****************
    DB_USER=pjeczadmin
    DB_PASS=********
    DB_NAME=pjecz_plataforma_web
    DB_HOST=127.0.0.1

Crear su archivo de configuración instance/settings.py

    SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxx'

Ejemplo para SQLLite

    SQLALCHEMY_DATABASE_URI = 'sqlite:///pjecz_tres_de_tres.sqlite3'

Ejemplo para PostgreSQL que obtiene datos de las varaibles de entorno

    import os
    DB_USER = os.environ.get("DB_USER", "wronguser")
    DB_PASS = os.environ.get("DB_PASS", "badpassword")
    DB_NAME = os.environ.get("DB_NAME", "pjecz_tres_de_tres")
    DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
    SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

Ejemplo para MariaDB en Justicia (172.30.37.233)

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://wronguser:badpassword@172.30.37.233/pjecz_tres_de_tres'

## Cargar registros iniciales

Crear directorio seed

    mkdir seed

Copiar archivos CSV desde Archivista y ponerlos en seed. Ejecutar...

    pip install --editable .
    plataforma_web db inicializar
    plataforma_web db alimentar

En el futuro, use reiniciar que es inicializar y alimentar

    plataforma_web db reiniciar

## Pasos para arrancar el sistema web

En el entorno virtual cargue las variables de entorno

Para la línea de comandos de windows...

    set FLASK_APP=plataforma_web/app.py
    set FLASK_DEBUG=1

Para la power shell de windows...

    $env:FLASK_APP = "plataforma_web/app.py"
    $env:FLASK_DEBUG = 1

Para la terminal GNU/Linux...

    FLASK_APP=plataforma_web.app
    FLASK_DEBUG=1

Y ejecute Flask

    flask run

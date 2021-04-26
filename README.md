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

    # Flask
    FLASK_APP=plataforma_web.app
    FLASK_DEBUG=1
    SECRET_KEY=****************

O crear archivo instance/settings.py que defina...

    # Flask
    SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxx'

    # Base de datos en SQLLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///pjecz_tres_de_tres.sqlite3'

Ejemplo para PostgreSQL, agregue en .env los datos de conexión

    # Base de datos local
    DB_USER=pjeczadmin
    DB_PASS=********
    DB_NAME=pjecz_plataforma_web
    DB_HOST=127.0.0.1

Y los obtiene por variables de entorno en instace/settings.py

    import os
    DB_USER = os.environ.get("DB_USER", "wronguser")
    DB_PASS = os.environ.get("DB_PASS", "badpassword")
    DB_NAME = os.environ.get("DB_NAME", "pjecz_plataforma_web")
    DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
    SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

Ejemplo para MariaDB en Justicia (172.30.37.233)

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://wronguser:badpassword@172.30.37.233/pjecz_plataforma_web'

## Cargar registros iniciales

Crear directorio seed

    mkdir seed

Copiar archivos CSV desde Archivista y ponerlos en seed. Ejecutar...

    pip install --editable .
    plataforma_web db inicializar
    plataforma_web db alimentar

En el futuro, use reiniciar que es inicializar y alimentar

    plataforma_web db reiniciar

## Arrancar el Flask

En el entorno virtual cargue las variables de entorno

Para la línea de comandos de windows...

    set FLASK_APP=plataforma_web/app.py
    set FLASK_DEBUG=1

Para la power shell de windows...

    $env:FLASK_APP = "plataforma_web/app.py"
    $env:FLASK_DEBUG = 1

Para la terminal GNU/Linux...

    export FLASK_APP=plataforma_web.app
    export FLASK_DEBUG=1

Y ejecute Flask

    flask run

## Configurar VSCode

Aparte de su configuració particular, agregue el archivo .vscode/settings.json con

    {
        "editor.formatOnSave": true,
        "python.formatting.provider": "black",
        "python.formatting.blackArgs": ["--line-length", "256"],
        "python.linting.pylintArgs": ["--max-line-length", "256", "--load-plugins", "pylint_flask_sqlalchemy"]
    }

Esto habilita

- El formateo del código con [Black](https://black.readthedocs.io/en/stable/)
- Líneas más largas de hasta 256 caracteres
- Reconocimiento de sintaxis de Flask SQLAlchemy

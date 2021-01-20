# pjecz-plataforma-web

Administrador de contenidos del sitio web del PJECZ.

## Pasos para preparar el Entorno Virtual

Crear el enorno virtual dentro de la copia local del repositorio

    python -m venv venv

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

## Pasos para configurar para desarrollo local

Crear su archivo de configuración config/settings.py

    # Siempre en falso
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret key
    SECRET_KEY = 'xxxxxxxxxxxxxxxxxxxxxxx'

    # SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///pjecz_plataforma_web.sqlite3'

## Pasos para inicializar la base de datos

Dentro del entorno virtual, instale el script con...

    pip install --editable .

Pruebe que funcione

    plataforma_web --help

Para inicializar la base de datos

    plataforma_web db inicializar

Copie los archivos CSV desde archivista a seed

Alimentar la base de datos con

    plataforma_web db alimentar

Para su conocimiento, reiniciar es inicializar y alimentar

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

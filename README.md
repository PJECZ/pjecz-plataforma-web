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

Instale el script click

Copie los archivos CSV que alimentan la base de datos

Inicializar la base de datos

Alimentar la base de datos

# pjecz-plataforma-web

Administrador de contenidos del sitio web del PJECZ.

## Entorno Virtual con Python 3.8

Crear el entorno virtual dentro de la copia local del repositorio, con

    python3.8 -m venv venv

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

Instalar el Comando Cli

    pip install --editable .

## Configurar

Debe crear un archivo `instance/settings.py` que defina su conexion a la base de datos...

    """
    Configuracion para desarrollo
    """
    import os


    # Base de datos
    DB_USER = os.environ.get("DB_USER", "wronguser")
    DB_PASS = os.environ.get("DB_PASS", "badpassword")
    DB_NAME = os.environ.get("DB_NAME", "pjecz_plataforma_web")
    DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
    DB_PORT = os.environ.get("DB_PORT", "5432")

    # PostgreSQL
    SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

Guarde sus configuraciones, contrasenas y tokens en un archivo `.env`

    # Flask, para SECRET_KEY use openssl rand -hex 24
    FLASK_APP=plataforma_web.app
    FLASK_DEBUG=1
    SECRET_KEY=XXXXXXXXXXXXXXXX

    # Base de datos
    DB_HOST=127.0.0.1
    DB_PORT=8432
    DB_NAME=pjecz_plataforma_web
    DB_USER=adminpjeczplataformaweb
    DB_PASS=XXXXXXXXXXXXXXXX

    # Redis
    REDIS_URL=redis://127.0.0.1
    TASK_QUEUE=pjecz_plataforma_web

    # Google Cloud Storage
    CLOUD_STORAGE_DEPOSITO=

    # Host
    HOST=

    # Salt sirve para cifrar el ID con HashID, debe ser igual en la API
    SALT=XXXXXXXXXXXXXXXX

    # Sendgrid
    SENDGRID_API_KEY=
    SENDGRID_FROM_EMAIL=
    SENDGRID_TO_EMAIL_REPORTES=

    # Financieros Vales
    FIN_VALES_EFIRMA_SER_FIRMA_CADENA_URL=
    FIN_VALES_EFIRMA_CAN_FIRMA_CADENA_URL=
    FIN_VALES_EFIRMA_QR_URL=
    FIN_VALES_EFIRMA_APP_ID=
    FIN_VALES_EFIRMA_APP_PASS=

    # RRHH Personal API OAuth2
    RRHH_PERSONAL_API_URL=
    RRHH_PERSONAL_API_USERNAME=
    RRHH_PERSONAL_API_PASSWORD=

    # Si esta en PRODUCTION se evita reiniciar la base de datos
    DEPLOYMENT_ENVIRONMENT=develop

Cree el archivo `.bashrc` para que un perfil de Konsole le facilite la inicializacion

    # pjecz-plataforma-web

    if [ -f ~/.bashrc ]
    then
        . ~/.bashrc
    fi

    if command -v figlet &> /dev/null
    then
        figlet PJECZ Plataforma Web
    else
        echo "== PJECZ Plataforma Web"
    fi
    echo

    if [ -f .env ]
    then
        echo "-- Variables de entorno"
        export $(grep -v '^#' .env | xargs)
        echo "   CLOUD_STORAGE_DEPOSITO: ${CLOUD_STORAGE_DEPOSITO}"
        echo "   DEPLOYMENT_ENVIRONMENT: ${DEPLOYMENT_ENVIRONMENT}"
        echo "   DB_HOST: ${DB_HOST}"
        echo "   DB_PORT: ${DB_PORT}"
        echo "   DB_NAME: ${DB_NAME}"
        echo "   DB_USER: ${DB_USER}"
        echo "   DB_PASS: ${DB_PASS}"
        echo "   FLASK_APP: ${FLASK_APP}"
        echo "   HOST: ${HOST}"
        echo "   REDIS_URL: ${REDIS_URL}"
        echo "   SALT: ${SALT}"
        echo "   SECRET_KEY: ${SECRET_KEY}"
        echo "   TASK_QUEUE: ${TASK_QUEUE}"
        echo
        export PGHOST=$DB_HOST
        export PGPORT=5432
        export PGDATABASE=$DB_NAME
        export PGUSER=$DB_USER
        export PGPASSWORD=$DB_PASS
    fi

    if [ -d venv ]
    then
        echo "-- Python Virtual Environment"
        source venv/bin/activate
        echo "   $(python3 --version)"
        export PYTHONPATH=$(pwd)
        echo "   PYTHONPATH: ${PYTHONPATH}"
        echo
        echo "-- Ejecutar Flask o RQ Worker"
        alias arrancar="flask run --host 0.0.0.0 --port=5003"
        alias fondear="rq worker ${TASK_QUEUE}"
        echo "   arrancar = flask run --host 0.0.0.0 --port=5003"
        echo "   fondear = rq worker ${TASK_QUEUE}"
        echo
    fi

    if [ -f app.yaml ]
    then
        echo "-- Subir a Google Cloud"
        echo "   gcloud app deploy"
        echo
    fi

## Arrancar Flask

Abra una terminal, cargue el entorno virtual y arranque Flask

    source .bashrc
    arrancar

## Arrancar RQ worker

Las tareas en el fondo requieren un servicio Redis

Abra una terminal, cargue el entorno virtual y deje en ejecución el worker

    source .bashrc
    fondear

Estará vigilante de Redis

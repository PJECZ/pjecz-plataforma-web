"""
Configuración para producción
"""
import os


# Google Cloud SQL
DB_USER = os.environ.get("DB_USER", "nouser")
DB_PASS = os.environ.get("DB_PASS", "wrongpassword")
DB_NAME = os.environ.get("DB_NAME", "pjecz_plataforma_web")
DB_SOCKET_DIR = os.environ.get("DB_SOCKET_DIR", "/cloudsql")
CLOUD_SQL_CONNECTION_NAME = os.environ.get("CLOUD_SQL_CONNECTION_NAME", "none")

# Google Cloud SQL MySQL anterior proyecto
# SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASS}@/{DB_NAME}?unix_socket={DB_SOCKET_DIR}/{CLOUD_SQL_CONNECTION_NAME}"

# Google Cloud SQL PostgreSQL nuevo proyecto justicia-digital-gob-mx
SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@/{DB_NAME}?unix_socket={DB_SOCKET_DIR}/{CLOUD_SQL_CONNECTION_NAME}"

# Always in False
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Secret key
SECRET_KEY = os.environ.get("SECRET_KEY", "Esta es una muy mala cadena aleatoria")

# Redis
REDIS_URL = os.environ.get("REDIS_URL", "redis://")
TASK_QUEUE = os.environ.get("TASK_QUEUE", "pjecz_plataforma_web")

# Google Cloud Storage
CLOUD_STORAGE_DEPOSITO = os.environ.get("CLOUD_STORAGE_DEPOSITO", "pjecz-pruebas")

# Host, para los vínculos en los mensajes como <HOST>/ficha/<HASHID>
HOST = os.environ.get("HOST", "https://plataforma-web.justiciadigital.gob.mx")

# Salt para convertir/reconverir el id en hash
SALT = os.environ.get("SALT", "Esta es una muy mala cadena aleatoria")

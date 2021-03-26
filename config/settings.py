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
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASS}@/{DB_NAME}?unix_socket={DB_SOCKET_DIR}/{CLOUD_SQL_CONNECTION_NAME}"

# Always in False
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Secret key
SECRET_KEY = os.environ.get("SECRET_KEY")

# Redis
REDIS_URL = os.environ.get("REDIS_URL", "redis://")
TASK_QUEUE = os.environ.get("TASK_QUEUE", "pjecz_plataforma_web")

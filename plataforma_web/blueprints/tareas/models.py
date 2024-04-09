"""
Tareas, modelos
"""

from flask import current_app
import redis
import rq
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Tarea(db.Model, UniversalMixin):
    """Tarea"""

    # Nombre de la tabla
    __tablename__ = "tareas"

    # Clave primaria
    id = db.Column(db.String(36), primary_key=True)

    # Clave foránea
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="tareas")

    # Columnas
    archivo = db.Column(db.String(256), nullable=False, default="", server_default="")
    comando = db.Column(db.String(256), nullable=False, index=True)
    ha_terminado = db.Column(db.Boolean, nullable=False, default=False)
    mensaje = db.Column(db.String(1024), nullable=False, default="", server_default="")
    url = db.Column(db.String(512), nullable=False, default="", server_default="")

    @property
    def nombre(self):
        """Antes la columna comando era nombre"""
        return self.comando

    @property
    def descripcion(self):
        """Antes la columna mensaje era descripcion"""
        return self.mensaje

    def get_rq_job(self):
        """Helper method that loads the RQ Job instance"""
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        """Returns the progress percentage for the task"""
        job = self.get_rq_job()
        return job.meta.get("progress", 0) if job is not None else 100

    def __repr__(self):
        """Representación"""
        return f"<Tarea {self.nombre}>"

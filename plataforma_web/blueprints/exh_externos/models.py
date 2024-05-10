"""
Exh Externos, modelos
"""

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class ExhExterno(db.Model, UniversalMixin):
    """ExhExterno"""

    # Nombre de la tabla
    __tablename__ = "exh_externos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    clave = db.Column(db.String(16), unique=True, nullable=False)
    descripcion = db.Column(db.String(256), nullable=False)
    api_key = db.Column(db.String(128))

    # Endpoints
    endpoint_consultar_materias = db.Column(db.String(1024))
    endpoint_recibir_exhorto = db.Column(db.String(1024))
    endpoint_recibir_exhorto_archivo = db.Column(db.String(1024))
    endpoint_consultar_exhorto = db.Column(db.String(1024))
    endpoint_recibir_respuesta_exhorto = db.Column(db.String(1024))
    endpoint_recibir_respuesta_exhorto_archivo = db.Column(db.String(1024))
    endpoint_actualizar_exhorto = db.Column(db.String(1024))
    endpoint_recibir_promocion = db.Column(db.String(1024))
    endpoint_recibir_promocion_archivo = db.Column(db.String(1024))

    def __repr__(self):
        """Representación"""
        return f"<ExhExterno> {self.clave}"

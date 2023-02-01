"""
Notarías Mensajes, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class NotMensaje(db.Model, UniversalMixin):
    """NotMensaje"""

    # Nombre de la tabla
    __tablename__ = "not_mensajes"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="not_mensajes")
    not_conversacion_id = db.Column(db.Integer, db.ForeignKey("not_conversaciones.id"), index=True, nullable=False)
    not_conversacion = db.relationship("NotConversacion", back_populates="not_mensajes")

    # Columnas
    contenido = db.Column(db.String(256), nullable=False)
    leido = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        """Representación"""
        return f"<NotMensaje {self.id}>"

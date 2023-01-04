"""
Escrituras Mensajes, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class NotMensajeEscritura(db.Model, UniversalMixin):
    """Mensaje Escritura"""

    # Nombre de la tabla
    __tablename__ = "not_mensajes_escrituras"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="not_mensajes_escrituras")
    not_conversacion_escritura_id = db.Column(db.Integer, db.ForeignKey("not_conversaciones_escrituras.id"), index=True, nullable=False)
    not_conversacion_escritura = db.relationship("NotConversacionEscritura", back_populates="not_mensajes_escrituras")

    # Columnas
    contenido = db.Column(db.String(256), nullable=False)
    leido = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        """Representación"""
        return f"<MensajeRespuesta {self.id}>"

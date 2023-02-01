"""
Notarías Conversaciones, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class NotConversacion(db.Model, UniversalMixin):
    """NotConversacion"""

    ESTADOS = OrderedDict(
        [
            ("ARCHIVADO", "Archivado"),
            ("ACTIVO", "Activo"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "not_conversaciones"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autor_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autor = db.relationship("Autoridad", back_populates="not_conversaciones")

    # Columnas
    destinatario_id = db.Column(db.Integer, nullable=False)
    leido = db.Column(db.Boolean, nullable=False, default=False)
    estado = db.Column(db.Enum(*ESTADOS, name="estados", native_enum=False), nullable=False)
    ultimo_mensaje_id = db.Column(db.Integer, nullable=True)

    # Hijos
    not_mensajes = db.relationship("NotMensaje", back_populates="not_conversacion", lazy="noload")

    def __repr__(self):
        """Representación"""
        return f"<NotConversacion {self.id}>"

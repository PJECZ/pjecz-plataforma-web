"""
Notarías Conversaciones, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class NotConversacion(db.Model, UniversalMixin):
    """Conversación"""

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
    autor = db.relationship("Autoridad", foreign_keys="NotConversacion.autor_id")
    destinatario_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    destinatario = db.relationship("Autoridad", foreign_keys="NotConversacion.destinatario_id")

    # Columnas
    leido = db.Column(db.Boolean, nullable=False, default=False)
    estado = db.Column(db.Enum(*ESTADOS, name="estados", native_enum=False), nullable=False)
    ultimo_mensaje_id = db.Column(db.Integer, nullable=True)

    # Hijos
    not_mensajes = db.relationship("NotMensaje", back_populates="not_conversacion", lazy="noload")

    def __repr__(self):
        """Representación"""
        return f"<Conversación {self.id}>"

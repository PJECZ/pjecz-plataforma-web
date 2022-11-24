"""
Mensajes, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class NotMsgConversacion(db.Model, UniversalMixin):
    """Conversación"""

    ESTADOS = OrderedDict(
        [
            ("ARCHIVADO", "Archivado"),
            ("ACTIVO", "Activo"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "not_msg_conversaciones"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autor_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autor = db.relationship("Autoridad", foreign_keys="NotMsgConversacion.autor_id")
    destinatario_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    destinatario = db.relationship("Autoridad", foreign_keys="NotMsgConversacion.destinatario_id")

    # Columnas
    leido = db.Column(db.Boolean, nullable=False, default=False)
    estado = db.Column(db.Enum(*ESTADOS, name="estados", native_enum=False), nullable=False)
    ultimo_mensaje_id = db.Column(db.Integer, nullable=True)

    # Hijos
    mensajes = db.relationship("NotMsgMensaje", back_populates="not_msg_conversacion", lazy="noload")

    def __repr__(self):
        """Representación"""
        return f"<Conversación {self.id}>"


class NotMsgMensaje(db.Model, UniversalMixin):
    """Mensaje"""

    # Nombre de la tabla
    __tablename__ = "not_msg_mensajes"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="mensajes")
    not_msg_conversacion_id = db.Column(db.Integer, db.ForeignKey("not_msg_conversaciones.id"), index=True, nullable=False)
    not_msg_conversacion = db.relationship("NotMsgConversacion", back_populates="mensajes")

    # Columnas
    contenido = db.Column(db.String(256), nullable=False)
    leido = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        """Representación"""
        return f"<MensajeRespuesta {self.id}>"

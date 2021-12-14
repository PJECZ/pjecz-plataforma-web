"""
Mensajes, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Mensaje(db.Model, UniversalMixin):
    """Mensaje"""

    # Nombre de la tabla
    __tablename__ = "mensajes"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    #destinatario_id = db.Column(db.Integer, db.ForeignKey("mensajes.id"), index=True, nullable=False)
    #destinatario = db.relationship("Usuario", back_populates="respuestas")

    # Columnas
    autor = db.Column(db.String(256), nullable=False)
    destinatario = db.Column(db.String(256), nullable=False)
    asunto = db.Column(db.String(128), nullable=False)
    contenido = db.Column(db.String(512), nullable=False)
    leido = db.Column(db.Boolean, nullable=False, default=False)

    # Hijos
    respuestas = db.relationship("MensajeRespuesta", back_populates="respuesta")

    def __repr__(self):
        """Representación"""
        return f"<Mensaje> {self.id}"



class MensajeRespuesta(db.Model, UniversalMixin):
    """Mensaje de Repuesta"""

    # Nombre de la tabla
    __tablename__ = "mensajes_respuestas"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    #autor_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    #autor = db.relationship("Usuario", back_populates="mensajes")
    respuesta_id = db.Column(db.Integer, db.ForeignKey("mensajes.id"), index=True, nullable=False)
    respuesta = db.relationship("Mensaje", back_populates="respuestas")

    # Columnas
    autor = db.Column(db.String(256), nullable=False)
    asunto = db.Column(db.String(128), nullable=False)
    contenido = db.Column(db.String(512), nullable=False)
    leido = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        """Representación"""
        return f"<Mensaje> {self.id}"

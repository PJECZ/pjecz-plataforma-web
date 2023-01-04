"""
not_conversaciones_escrituras, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class NotConversacionEscritura(db.Model, UniversalMixin):
    """NotConversacionEscritura"""

    ESTADOS = OrderedDict(
        [
            ("ARCHIVADO", "Archivado"),
            ("ACTIVO", "Activo"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "notconversacionesescrituras"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    # autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridad_id.id"), index=True, nullable=False)
    # autoridad = db.relationship("Autoridad", back_populates="not_conversaciones_escrituras")
    autor_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autor = db.relationship("Autoridad", foreign_keys="NotConversacionEscritura.autor_id")
    destinatario_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    destinatario = db.relationship("Autoridad", foreign_keys="NotConversacionEscritura.destinatario_id")

    # Columnas
    leido = db.Column(db.String(256), unique=True, nullable=False)
    estado = db.Column(db.Enum(*ESTADOS, name="estados", native_enum=False), nullable=False)
    ultimo_mensaje_id = db.Column(db.Integer, nullable=True)

    # Hijos
    not_escritura_id = db.relationship("NotEscritura", back_populates="not_conversacion_escritura", lazy="noload")

    def __repr__(self):
        """Representación"""
        return "<NotConversacionEscritura>"

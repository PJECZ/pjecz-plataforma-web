"""
not_conversaciones_escrituras, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class NotConversacionEscritura(db.Model, UniversalMixin):
    """NotConversacionEscritura"""

    # Nombre de la tabla
    __tablename__ = "notconversacionesescrituras"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridad_id.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="notconversacionesescrituras")

    # Columnas
    notaria = db.Column(db.String(256), unique=True, nullable=False)
    juzgado = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        """Representación"""
        return "<NotConversacionEscritura>"

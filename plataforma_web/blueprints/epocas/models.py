"""
Epocas, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Epoca(db.Model, UniversalMixin):
    """Epoca"""

    # Nombre de la tabla
    __tablename__ = "epocas"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    nombre = db.Column(db.String(256), unique=True, nullable=False)

    # Hijos
    tesis_jurisprudencias = db.relationship("TesisJurisprudencia", back_populates="epoca")

    def __repr__(self):
        """Representación"""
        return "<Epoca>"

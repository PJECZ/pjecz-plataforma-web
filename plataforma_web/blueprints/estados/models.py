"""
Estados, modelos
"""

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Estado(db.Model, UniversalMixin):
    """Estado"""

    # Nombre de la tabla
    __tablename__ = "estados"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    clave = db.Column(db.String(2), nullable=False, unique=True)
    nombre = db.Column(db.String(256), nullable=False)

    # Hijos
    municipios = db.relationship("Municipio", back_populates="estado")

    def __repr__(self):
        """Representación"""
        return f"<Estado {self.clave}>"

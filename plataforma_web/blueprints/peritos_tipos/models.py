"""
Peritos Tipos, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class PeritoTipo(db.Model, UniversalMixin):
    """PeritoTipo"""

    # Nombre de la tabla
    __tablename__ = "peritos_tipos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    nombre = db.Column(db.String(256), unique=True, nullable=False)

    # Hijos
    peritos = db.relationship("Perito", back_populates="perito_tipo")

    def __repr__(self):
        """Representación"""
        return f"<PeritoTipo {self.nombre}>"

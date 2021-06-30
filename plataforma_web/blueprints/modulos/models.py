"""
Modulos, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Modulo(db.Model, UniversalMixin):
    """Modulo"""

    # Nombre de la tabla
    __tablename__ = "modulos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    nombre = db.Column(db.String(256), unique=True, nullable=False)

    # Hijos
    resultados = db.relationship("Resultado", back_populates="modulo")

    def __repr__(self):
        """Representación"""
        return "f<Modulo {self.nombre}>"

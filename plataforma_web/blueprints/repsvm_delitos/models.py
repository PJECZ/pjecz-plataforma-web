"""
REPSVM Delitos, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class REPSVMDelito(db.Model, UniversalMixin):
    """REPSVMDelito"""

    # Nombre de la tabla
    __tablename__ = "repsvm_delitos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    nombre = db.Column(db.String(256), unique=True, nullable=False)

    # Hijos
    repsvm_agresores_delitos = db.relationship("REPSVMAgresoresDelitos", back_populates="repsvm_delitos")

    def __repr__(self):
        """Representación"""
        return "<REPSVMDelito>"

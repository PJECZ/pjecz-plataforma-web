"""
INV REDES, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class INVRedes(db.Model, UniversalMixin):
    """INVRedes"""

    # Nombre de la tabla
    __tablename__ = "inv_redes"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea

    # Columnas
    nombre = db.Column(db.String(256), unique=True, nullable=False)
    tipo = db.Column(db.String(256), nullable=False)

    # Hijos

    def __repr__(self):
        """Representación"""
        return "<INVRedes>"

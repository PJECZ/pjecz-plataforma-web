"""
Inventarios Marcas, modelos
"""

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class InvMarca(db.Model, UniversalMixin):
    """InvMarca"""

    # Nombre de la tabla
    __tablename__ = "inv_marcas"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea

    # Columnas
    nombre = db.Column(db.String(256), unique=True, nullable=False)

    # Hijos
    inv_modelos = db.relationship("InvModelo", back_populates="inv_marca", lazy="noload")

    def __repr__(self):
        """Representación"""
        return "<InvMarca>"

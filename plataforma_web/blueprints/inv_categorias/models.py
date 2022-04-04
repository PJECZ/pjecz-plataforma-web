"""
Inventarios Categorías, modelos
"""

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class InvCategoria(db.Model, UniversalMixin):
    """InvCategoria"""

    # Nombre de la tabla
    __tablename__ = "inv_categorias"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea

    # Columnas
    nombre = db.Column(db.String(256), unique=True, nullable=False)

    # Hijos
    inv_componentes = db.relationship("InvComponente", back_populates="inv_categoria", lazy="noload")

    def __repr__(self):
        """Representación"""
        return "<InvCategoria>"

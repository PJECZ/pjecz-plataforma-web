"""
Inventarios Categorias, modelos
"""

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class INVCategorias(db.Model, UniversalMixin):
    """INVCategorias"""

    # Nombre de la tabla
    __tablename__ = "inv_categorias"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea

    # Columnas
    nombre = db.Column(db.String(256), unique=True, nullable=False)

    # Hijos
    componentes = db.relationship("INVComponentes", back_populates="categoria")

    def __repr__(self):
        """Representación"""
        return "<INVCategorias>"

"""
Inventarios Componentes, modelos
"""

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class INVComponentes(db.Model, UniversalMixin):
    """INVComponentes"""

    # Nombre de la tabla
    __tablename__ = "inv_componentes"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    categoria_id = db.Column(db.Integer, db.ForeignKey("inv_categorias.id"), index=True, nullable=False)
    categoria = db.relationship("INVCategorias", back_populates="componentes")
    # equipo_id = db.Column(db.Integer, db.ForeignKey("inv_equipos.id"), index=True, nullable=False)
    # equipo = db.relationship("INVEquipos", back_populates="componentes")

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    cantidad = db.Column(db.Integer())
    version = db.Column(db.String(256))

    # Hijos

    def __repr__(self):
        """Representación"""
        return "<INVComponentes>"

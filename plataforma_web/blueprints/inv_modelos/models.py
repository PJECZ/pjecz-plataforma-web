"""
INV MODELOS, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class INVModelo(db.Model, UniversalMixin):
    """INVModelo"""

    # Nombre de la tabla
    __tablename__ = "inv_modelos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    marca_id = db.Column(db.Integer, db.ForeignKey("inv_marcas.id"), index=True, nullable=False)
    marca = db.relationship("INVMarca", back_populates="modelos")

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)

    # Hijos
    equipos = db.relationship("INVEquipo", back_populates="modelo")

    def __repr__(self):
        """Representación"""
        return "<INVModelo>"

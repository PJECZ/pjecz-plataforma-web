"""
Inventarios Modelos, modelos
"""

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class InvModelo(db.Model, UniversalMixin):
    """InvModelo"""

    # Nombre de la tabla
    __tablename__ = "inv_modelos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    inv_marca_id = db.Column(db.Integer, db.ForeignKey("inv_marcas.id"), index=True, nullable=False)
    marca = db.relationship("InvMarca", back_populates="modelos")

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)

    # Hijos
    equipos = db.relationship("InvEquipo", back_populates="modelo")

    @property
    def marca_modelo(self):
        """Junta marca y modelo"""
        return self.marca.nombre + " - " + self.descripcion

    def __repr__(self):
        """Representación"""
        return "<InvModelo>"

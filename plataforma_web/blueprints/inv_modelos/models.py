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
    inv_marca = db.relationship("InvMarca", back_populates="inv_modelos")

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)

    # Hijos
    inv_equipos = db.relationship("InvEquipo", back_populates="inv_modelo", lazy="noload")

    @property
    def marca_modelo(self):
        """Junta marca y modelo"""
        return self.inv_marca.nombre + " - " + self.descripcion

    def __repr__(self):
        """Representación"""
        return f"<InvModelo {self.id}>"

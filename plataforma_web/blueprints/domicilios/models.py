"""
Domicilios, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Domicilio(db.Model, UniversalMixin):
    """Domicilio"""

    # Nombre de la tabla
    __tablename__ = "domicilios"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea

    # Columnas
    colonia = db.Column(db.String(256), nullable=False)
    calle = db.Column(db.String(256), nullable=False)
    cp = db.Column(db.Integer())
    num_ext = db.Column(db.Integer())
    num_int = db.Column(db.Integer())

    # Hijos
    cit_clientes = db.relationship("CitCliente", back_populates="domicilio")
    oficinas = db.relationship("Oficina", back_populates="domicilio")

    def __repr__(self):
        """Representación"""
        return "<Domicilio>"

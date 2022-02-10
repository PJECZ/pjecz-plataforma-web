"""
Soportes Categorias, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class SoporteCategoria(db.Model, UniversalMixin):
    """SoporteCategoria"""

    # Nombre de la tabla
    __tablename__ = "soportes_categorias"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    nombre = db.Column(db.String(256), unique=True, nullable=False)
    instrucciones = db.Column(db.Text())

    # Hijos
    soportes_tickets = db.relationship("SoporteTicket", back_populates="soporte_categoria")

    def __repr__(self):
        """Representación"""
        return "<SoporteCategoria>"

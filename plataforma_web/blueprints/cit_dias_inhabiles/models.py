"""
Cit Días Inhabiles, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class CitDiaInhabil(db.Model, UniversalMixin):
    """CitDiaInhabil"""

    # Nombre de la tabla
    __tablename__ = "cit_dias_inhabiles"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    fecha = db.Column(db.Date(), nullable=False)
    descripcion = db.Column(db.String(512), nullable=True)

    def __repr__(self):
        """Representación"""
        return "<CitDiaInhabil>"

"""
Exh Areas, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class ExhArea(db.Model, UniversalMixin):
    """ Area """

    # Nombre de la tabla
    __tablename__ = 'exh_areas'

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    clave = db.Column(db.String(64), unique=True, nullable=False)
    nombre = db.Column(db.String(128), unique=True, nullable=False)

    def __repr__(self):
        """ Representación """
        return '<ExhArea> {self.id}'

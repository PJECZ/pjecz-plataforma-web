"""
Abogados, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Abogado(db.Model, UniversalMixin):
    """ Abogado """

    # Nombre de la tabla
    __tablename__ = 'abogados'

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    nombre = db.Column(db.String(256), unique=True, nullable=False)
    descripcion = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        """ Representación """
        return f'<Abogado {self.nombre}>'

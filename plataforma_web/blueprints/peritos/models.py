"""
Peritos, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Perito(db.Model, UniversalMixin):
    """ Perito """

    # Nombre de la tabla
    __tablename__ = 'peritos'

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    tipo = db.Column(db.String(256), nullable=False)
    nombre = db.Column(db.String(256), nullable=False)
    domicilio = db.Column(db.String(256), nullable=False)
    telefono_fijo = db.Column(db.String(256))
    telefono_celular = db.Column(db.String(256))
    email = db.Column(db.String(256))

    def __repr__(self):
        """ Representación """
        return f'<Perito {self.nombre}>'

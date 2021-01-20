"""
Edictos, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Edicto(db.Model, UniversalMixin):
    """ Edicto """

    # Nombre de la tabla
    __tablename__ = 'edictos'

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    archivo = db.Column(db.String(256), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    descripcion = db.Column(db.String(256), nullable=False)
    expediente = db.Column(db.String(256))
    numero_publicacion = db.Column(db.Integer())
    url = db.Column(db.String(256))

    def __repr__(self):
        """ Representación """
        return f'<Edicto {self.nombre}>'

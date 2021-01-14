"""
Autoridades, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Autoridad(db.Model, UniversalMixin):
    """ Autoridad """

    # Nombre de la tabla
    __tablename__ = 'autoridades'

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256))

    # Clave foránea
    distrito_id = db.Column(
        'distrito',
        db.String(256),
        db.ForeignKey('distritos.id'),
        index=True,
        nullable=False
    )

    def __repr__(self):
        """ Representación """
        return f'<Autoridad {self.descripcion}>'

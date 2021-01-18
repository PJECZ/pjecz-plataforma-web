"""
Glosas, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Glosa(db.Model, UniversalMixin):
    """ Glosa """

    # Nombre de la tabla
    __tablename__ = 'glosas'

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autoridad_id = db.Column(
        'autoridad',
        db.Integer,
        db.ForeignKey('autoridades.id'),
        index=True,
        nullable=False
    )

    # Columnas
    fecha = db.Column(db.Date, nullable=False)
    juicio_tipo = db.Column(db.String(256), nullable=False)
    expediente = db.Column(db.String(256), nullable=False)
    url = db.Column(db.String(256))

    def __repr__(self):
        """ Representación """
        return f'<Glosa {self.nombre}>'

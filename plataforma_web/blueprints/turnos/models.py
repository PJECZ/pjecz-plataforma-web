"""
Turnos, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Turnos(db.Model, UniversalMixin):
    """ Turnos """

    # Nombre de la tabla
    __tablename__ = 'turnos'

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    ventanilla_id = db.Column(db.Integer, db.ForeignKey('ventanillas.id'), index=True, nullable=False)
    ventanilla = db.relationship('Ventanilla', back_populates='turnos')

    # Columnas
    nombre = db.Column(db.String(256), unique=True, nullable=False)
    descripcion = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        """ Representación """
        return f'<Turnos>'

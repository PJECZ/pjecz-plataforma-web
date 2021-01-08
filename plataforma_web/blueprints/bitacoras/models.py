"""
Bitácoras, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Bitacora(db.Model, UniversalMixin):
    """ Bitacora """

    # Nombre de la tabla
    __tablename__ = 'bitacoras'

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    usuario_id = db.Column(
        'usuario',
        db.Integer,
        db.ForeignKey('usuarios.id'),
        index=True,
        nullable=False,
    )

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        """ Representación """
        return f'<Bitacora {self.creado} {self.descripcion}>'

"""
CITAS Expedientes, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class CITExpediente(db.Model, UniversalMixin):
    """ CITExpediente """

    # Nombre de la tabla
    __tablename__ = 'cit_expedientes'

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea

    # Columnas
    expediente = db.Column(db.String(16), nullable=False)

    # Hijos

    def __repr__(self):
        """ Representación """
        return '<Cit_Expediente>'

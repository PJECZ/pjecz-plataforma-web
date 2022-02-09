"""
CITAS Días Inhabiles, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class CITDiaInhabil(db.Model, UniversalMixin):
    """ CITDiaInhabil """

    # Nombre de la tabla
    __tablename__ = 'cit_dias_inhabiles'

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea

    # Columnas
    fecha = db.Column(db.Date(), nullable=False)
    descripcion = db.Column(db.String(512), nullable=True)

    # Hijos

    def __repr__(self):
        """ Representación """
        return '<CIT_DiaInhabil>'

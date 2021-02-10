"""
Ubicaciones de Expedientes, modelos
"""

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin

class UbicacionDeExpediente(db.Model, UniversalMixin):
    """ Ubicacion_Expediente """

    # Nombre de la tabla
    __tablename__ = 'ubicaciones_expedientes'

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    expediente = db.Column(db.String(256), nullable=False)
    ubicacion = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        """ Representación """
        return f'<Ubicacion_Expediente {self.nombre}>'




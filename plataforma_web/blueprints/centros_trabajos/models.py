"""
Centrso de Trabajos, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class CentroTrabajo(db.Model, UniversalMixin):
    """ CentroTrabajo """

    # Nombre de la tabla
    __tablename__ = 'centros_trabajos'

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    distrito_id = db.Column(db.Integer, db.ForeignKey("distritos.id"), index=True, nullable=False)
    distrito = db.relationship("Distrito", back_populates="centros_trabajos")

    # Columnas
    clave = db.Column(db.String(16), unique=True, nullable=False)
    nombre = db.Column(db.String(256), nullable=False)
    area = db.Column(db.String(256), nullable=False)

    # Hijos
    funcionarios = db.relationship('Funcionario', back_populates='centro_trabajo')

    def __repr__(self):
        """ Representación """
        return '<CentroTrabajo>'

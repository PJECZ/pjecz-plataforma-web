"""
Materias, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Materia(db.Model, UniversalMixin):
    """Materia"""

    # Nombre de la tabla
    __tablename__ = "materias"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    nombre = db.Column(db.String(64), unique=True, nullable=False)

    # Hijos
    autoridades = db.relationship("Autoridad", back_populates="materia", lazy="noload")
    # sentencias = db.relationship("Sentencia", back_populates="materia", lazy="noload")
    materias_tipos_juicios = db.relationship('MateriaTipojuicio', back_populates='materia')

    def __repr__(self):
        """Representación"""
        return "<Materia>"

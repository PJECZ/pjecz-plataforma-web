"""
Materias Tipo de Juicio, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class MateriaTipoJuicio(db.Model, UniversalMixin):
    """MateriaTipoJuicio"""

    # Nombre de la tabla
    __tablename__ = "materias_tipos_juicios"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    materia_id = db.Column(db.Integer, db.ForeignKey("materias.id"), index=True, nullable=False)
    materia = db.relationship("Materia", back_populates="tipos_juicios")

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)

    # Hijos
    sentencias = db.relationship("Sentencia", back_populates="materia_tipo_juicio")

    def __repr__(self):
        """Representación"""
        return f"<MateriaTipoJuicio>"

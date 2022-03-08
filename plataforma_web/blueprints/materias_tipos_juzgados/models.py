"""
Materias Tipos Juzgados, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class MateriaTipoJuzgado(db.Model, UniversalMixin):
    """MateriaTipoJuzgado"""

    # Nombre de la tabla
    __tablename__ = "materias_tipos_juzgados"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    materia_id = db.Column(db.Integer, db.ForeignKey("materias.id"), index=True, nullable=False)
    materia = db.relationship("Materia", back_populates="materias_tipos_juzgados")

    # Columnas
    clave = db.Column(db.String(256), unique=True, nullable=False)
    descripcion = db.Column(db.String(256), nullable=False)

    # Hijos
    repsvm_agresores = db.relationship("REPSVMAgresor", back_populates="materia_tipo_juzgado")

    def __repr__(self):
        """Representación"""
        return f"<MateriaTipoJuzgado {self.clave}>"

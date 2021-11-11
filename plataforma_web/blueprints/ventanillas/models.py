"""
Ventanillas, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Ventanilla(db.Model, UniversalMixin):
    """Ventanilla"""

    # Nombre de la tabla
    __tablename__ = "ventanillas"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="autoridades")

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    numero = db.Column(db.Integer(), nullable=False)

    # Hijos
    turnos = db.relationship("Turno", back_populates="ventanilla", lazy="noload")

    def __repr__(self):
        """Representación"""
        return f"<Ventanilla {self.descripcion}>"

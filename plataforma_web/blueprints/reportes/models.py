"""
Reportes, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Reporte(db.Model, UniversalMixin):
    """Reporte"""

    # Nombre de la tabla
    __tablename__ = "reportes"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    desde = db.Column(db.DateTime(), nullable=False)
    hasta = db.Column(db.DateTime(), nullable=False)

    # Hijos
    resultados = db.relationship("Resultado", back_populates="reporte")

    def __repr__(self):
        """Representación"""
        return f"<Reporte {self.descripcion}>"

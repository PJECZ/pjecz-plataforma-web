"""
Rep Graficas, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class RepGrafica(db.Model, UniversalMixin):
    """RepGrafica"""

    # Nombre de la tabla
    __tablename__ = "rep_graficas"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    nombre = db.Column(db.String(256), unique=True, nullable=False)

    # Hijos
    rep_reportes = db.relationship("RepReporte", back_populates="rep_grafica")

    def __repr__(self):
        """Representación"""
        return "<RepGrafica>"

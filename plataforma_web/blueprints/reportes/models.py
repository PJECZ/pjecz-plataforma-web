"""
Reportes, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Reportes(db.Model, UniversalMixin):
    """Reportes"""

    # Nombre de la tabla
    __tablename__ = "reportes"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="reportes")

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    desde = db.Column(db.DateTime(), nullable=False)
    hasta = db.Column(db.DateTime(), nullable=False)

    # Hijos
    resultados = db.relationship("Resultado", back_populates="reporte")

    def __repr__(self):
        """Representación"""
        return "<Reportes>"

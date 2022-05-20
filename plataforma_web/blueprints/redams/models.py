"""
REDAM (Registro Estatal de Deudores Alimentarios), modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Redam(db.Model, UniversalMixin):
    """Redam"""

    # Nombre de la tabla
    __tablename__ = "redam"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="redams")

    # Columnas
    nombre = db.Column(db.String(256), nullable=False)
    expediente = db.Column(db.String(16), index=True, nullable=False)
    fecha = db.Column(db.Date, index=True, nullable=False)
    observaciones = db.Column(db.String(1024), nullable=False)

    def __repr__(self):
        """Representación"""
        return f"<Redam {self.id}>"

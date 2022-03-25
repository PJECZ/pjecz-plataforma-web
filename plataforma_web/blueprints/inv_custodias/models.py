"""
Inventarios Custodias, modelos
"""

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class InvCustodia(db.Model, UniversalMixin):
    """InvCustodia"""

    # Nombre de la tabla
    __tablename__ = "inv_custodias"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="inv_custodias")

    # Columnas
    fecha = db.Column(db.Date, nullable=False, index=True)
    curp = db.Column(db.String(256), nullable=True)
    nombre_completo = db.Column(db.String(256))

    # Hijos
    equipos = db.relationship("InvEquipo", back_populates="inv_custodia")

    def __repr__(self):
        """Representación"""
        return "<InvCustodia>"

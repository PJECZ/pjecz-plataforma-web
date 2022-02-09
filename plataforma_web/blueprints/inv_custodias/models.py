"""
Inventarios Custodias, modelos
"""

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class INVCustodia(db.Model, UniversalMixin):
    """INVCustodia"""

    # Nombre de la tabla
    __tablename__ = "inv_custodias"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="custodias")
    # oficina_id = db.Column(db.Integer, db.ForeignKey("inv_equipos.id"), index=True, nullable=False)
    # oficina = db.relationship("Oficinas", back_populates="custodias")

    # Columnas
    fecha = db.Column(db.Date(), nullable=False)
    curp = db.Column(db.String(256), unique=True, nullable=False)
    nombre_completo = db.Column(db.String(256))

    # Hijos

    def __repr__(self):
        """Representación"""
        return "<INVCustodia>"

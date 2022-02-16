"""
INV FOTOS, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class INVEquipoFoto(db.Model, UniversalMixin):
    """INVEquipoFoto"""

    # Nombre de la tabla
    __tablename__ = "inv_equipos_fotos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foránea para el ticket
    equipo_id = db.Column(db.Integer, db.ForeignKey("inv_equipos.id"), index=True, nullable=True)
    equipo = db.relationship("INVEquipo", back_populates="fotos")

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    archivo = db.Column(db.String(256), nullable=False, default="", server_default="")
    url = db.Column(db.String(512), nullable=False, default="", server_default="")

    def __repr__(self):
        """Representación"""
        return "<INVEquipoFoto>"

"""
Inventarios Equipos Fotos, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class InvEquipoFoto(db.Model, UniversalMixin):
    """InvEquipoFoto"""

    # Nombre de la tabla
    __tablename__ = "inv_equipos_fotos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foránea para el ticket
    inv_equipo_id = db.Column(db.Integer, db.ForeignKey("inv_equipos.id"), index=True, nullable=False)
    inv_equipo = db.relationship("InvEquipo", back_populates="inv_equipos_fotos")

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    archivo = db.Column(db.String(256), nullable=False, default="", server_default="")
    url = db.Column(db.String(512), nullable=False, default="", server_default="")

    def __repr__(self):
        """Representación"""
        return "<InvEquipoFoto>"

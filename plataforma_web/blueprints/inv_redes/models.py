"""
INV REDES, modelos
"""

from collections import OrderedDict

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class INVRedes(db.Model, UniversalMixin):
    """INVRedes"""

    TIPOS = OrderedDict(
        [
            ("LAN", "Lan"),
            ("WIRELESS", "Wireless"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "inv_redes"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea

    # Columnas
    nombre = db.Column(db.String(256), unique=True, nullable=False)
    tipo = db.Column(db.Enum(*TIPOS, name="tipos_redes", native_enum=False), index=True, nullable=False)

    # Hijos
    equipos = db.relationship("INVEquipo", back_populates="red")

    def __repr__(self):
        """Representación"""
        return "<INVRedes>"

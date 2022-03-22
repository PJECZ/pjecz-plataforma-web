"""
Inventarios Redes, modelos
"""

from collections import OrderedDict

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class InvRed(db.Model, UniversalMixin):
    """InvRed"""

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
    equipos = db.relationship("InvEquipo", back_populates="red")

    def __repr__(self):
        """Representación"""
        return "<InvRed>"

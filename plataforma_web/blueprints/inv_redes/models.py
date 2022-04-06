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

    # Columnas
    nombre = db.Column(db.String(256), unique=True, nullable=False)
    tipo = db.Column(db.Enum(*TIPOS, name="tipos_redes", native_enum=False), index=True, nullable=False)

    # Hijos
    inv_equipos = db.relationship("InvEquipo", back_populates="inv_red", lazy="noload")

    def __repr__(self):
        """Representación"""
        return f"<InvRed {self.nombre}>"

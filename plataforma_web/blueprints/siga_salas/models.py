"""
SIGA Salas, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class SIGASala(db.Model, UniversalMixin):
    """SIGA Salas"""

    ESTADOS = OrderedDict(
        [
            ("OPERATIVO", "Operativo"),
            ("FUERA DE LINEA", "Fuera de línea"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "siga_salas"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    domicilio_id = db.Column(db.Integer, db.ForeignKey("domicilios.id"), index=True, nullable=False)
    domicilio = db.relationship("Domicilio", back_populates="siga_salas")

    # Columnas
    clave = db.Column(db.String(16), unique=True, nullable=False)
    direccion_ip = db.Column(db.String(16))
    direccion_nvr = db.Column(db.String(16))
    estado = db.Column(db.Enum(*ESTADOS, name="tipos_estados", native_enum=False), index=True, nullable=False)
    descripcion = db.Column(db.String(1024))

    # Hijos
    siga_bitacoras = db.relationship("SIGABitacora", back_populates="siga_sala", lazy="noload")

    @property
    def clave_nombre(self):
        """Entrega clave - descripción para usar en select"""
        return f"{self.clave} — {self.descripcion}"

    def __repr__(self):
        """Representación"""
        return f"<Sala {self.id}: {self.clave} — {self.descripcion}>"

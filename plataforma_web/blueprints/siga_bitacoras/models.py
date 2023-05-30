"""
SIGA Bitacoras, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class SIGABitacora(db.Model, UniversalMixin):
    """SIGA Salas"""

    ESTADOS = OrderedDict(
        [
            ("PENDIENTE", "Operación pendiente de realizar"),
            ("CORRECTO", "Operación terminada con éxito"),
            ("CANCELADO", "Operación cancelada"),
            ("ERROR", "Operación con error"),
        ]
    )

    ACCIONES = OrderedDict(
        [
            ("LEER NOMBRE", "Leer el nombre del archivo"),
            ("INSERT", "Crear nuevo registro en la tabla"),
            ("UPLOAD", "Copiar el archivo a GDrive"),
            ("METADATOS", "Lectura de metadatos del archivo"),
            ("UPDATE", "Se actualizó el registro"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "siga_bitacoras"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    siga_sala_id = db.Column(db.Integer, db.ForeignKey("siga_salas.id"), index=True, nullable=False)
    siga_sala = db.relationship("SIGASala", back_populates="siga_bitacoras")

    # Columnas
    accion = db.Column(db.Enum(*ACCIONES, name="tipos_acciones", native_enum=False), index=True, nullable=False)
    estado = db.Column(db.Enum(*ESTADOS, name="tipos_estados", native_enum=False), index=True, nullable=False)
    descripcion = db.Column(db.String(512))

    def __repr__(self):
        """Representación"""
        return f"<SIGA Bitacora {self.id}"

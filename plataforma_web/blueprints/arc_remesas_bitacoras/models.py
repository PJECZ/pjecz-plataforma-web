"""
Archivo Remesas Bitacoras, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class ArcRemesaBitacora(db.Model, UniversalMixin):
    """Archivo Remesas Bitácora"""

    ACCIONES = OrderedDict(  # varchar(24)
        [
            ("CREADA", "Creada"),
            ("MODIFICADA", "Modificada"),
            ("CANCELADA", "Cancelada"),
            ("ENVIADA", "Enviada"),
            ("ASIGNADA", "Asignar"),
            ("RECHAZADA", "Rechazada"),
            ("ARCHIVADA", "Archivada"),
            ("ARCHIVADA CON ANOMALIA", "Archivado con Anomalía"),  # El ARCHIVISTA termina de procesar la remesa pero almenos un documento presentó anomalía
            ("ANOMALIA GENERAL", "Anomalía General"),
            ("PASADA AL HISTORIAL", "Pasada al Historial"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "arc_remesas_bitacoras"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    arc_remesa_id = db.Column(db.Integer, db.ForeignKey("arc_remesas.id"), index=True, nullable=False)
    arc_remesa = db.relationship("ArcRemesa", back_populates="arc_remesas_bitacoras")
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="arc_remesas_bitacoras")

    # Columnas
    accion = db.Column(
        db.Enum(*ACCIONES, name="tipo_accion", native_enum=False),
        nullable=False,
    )
    observaciones = db.Column(db.String(256))

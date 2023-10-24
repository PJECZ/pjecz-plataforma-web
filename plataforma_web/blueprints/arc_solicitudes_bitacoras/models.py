"""
Archivo Solicitudes Bitácoras, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class ArcSolicitudBitacora(db.Model, UniversalMixin):
    """Archivo Solicitud Bitácora"""

    ACCIONES = OrderedDict(  # varchar(24)
        [
            ("SOLICITADA", "Solicitada"),
            ("CANCELADA", "Cancelada"),
            ("ASIGNADA", "Asignada"),
            ("ENCONTRADA", "Encontrada"),
            ("NO ENCONTRADA", "No Encontrada"),
            ("ENVIADA", "Enviada"),
            ("ENTREGADA", "Entregada"),
            ("PASADA AL HISTORIAL", "Pasa al historial"),
            ("ELIMINADA", "Eliminada"),
            ("RECUPERADA", "Recuperada"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "arc_solicitudes_bitacoras"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    arc_solicitud_id = db.Column(db.Integer, db.ForeignKey("arc_solicitudes.id"), index=True, nullable=False)
    arc_solicitud = db.relationship("ArcSolicitud", back_populates="arc_solicitudes_bitacoras")
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="arc_solicitudes_bitacoras")

    # Columnas
    accion = db.Column(
        db.Enum(*ACCIONES, name="tipo_accion", native_enum=False),
        nullable=False,
    )
    observaciones = db.Column(db.String(256))

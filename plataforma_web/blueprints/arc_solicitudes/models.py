"""
Archivo Documentos Solicitudes, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class ArcSolicitud(db.Model, UniversalMixin):
    """Archivo Documentos Solicitudes"""

    ESTADOS = OrderedDict(  # varchar(16)
        [
            ("SOLICITADO", "Solicitado"),
            ("CANCELADO", "Cancelado"),
            ("ASIGNADO", "Asignado"),
            ("ENCONTRADO", "Encontrado"),
            ("NO ENCONTRADO", "No Encontrado"),
            ("ENVIANDO", "Enviando"),
            ("ENTREGADO", "Entregado"),
        ]
    )

    RAZONES = OrderedDict(  # varchar(32)
        [
            ("FALTA DE ORIGEN", "Falta de Origen"),
            ("NO COINCIDEN LAS PARTES", "No coinciden las partes"),
            ("PRESTADO", "Prestado"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "arc_solicitudes"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    arc_documento_id = db.Column(db.Integer, db.ForeignKey("arc_documentos.id"), index=True, nullable=False)
    arc_documento = db.relationship("ArcDocumento", back_populates="arc_solicitudes")
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="arc_solicitudes")
    usuario_asignado_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True)
    usuario_asignado = db.relationship("Usuario", back_populates="arc_solicitudes_asignado")

    # Columnas
    usuario_receptor_id = db.Column(db.Integer)
    esta_archivado = db.Column(db.Boolean, nullable=False, default=False)
    num_folio = db.Column(db.String(16))
    tiempo_recepcion = db.Column(db.DateTime)
    fojas = db.Column(db.Integer)
    estado = db.Column(
        db.Enum(*ESTADOS, name="estados", native_enum=False),
        nullable=False,
    )
    razon = db.Column(db.Enum(*RAZONES, name="razon", native_enum=False))
    observaciones_solicitud = db.Column(db.String(256))
    observaciones_razon = db.Column(db.String(256))

    # Hijos
    arc_solicitudes_bitacoras = db.relationship("ArcSolicitudBitacora", back_populates="arc_solicitud", lazy="noload")

    def __repr__(self):
        """Representación"""
        return f"<Solicitud> {self.id}"

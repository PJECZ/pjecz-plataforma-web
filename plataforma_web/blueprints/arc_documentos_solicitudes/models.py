"""
Archivo Documentos Solicitudes, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin
from sqlalchemy.sql import func


class ArcDocumentoSolicitud(db.Model, UniversalMixin):
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
    __tablename__ = "arc_documentos_solicitudes"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    arc_documento_id = db.Column(db.Integer, db.ForeignKey("arc_documentos.id"), index=True, nullable=False)
    arc_documento = db.relationship("ArcDocumento", back_populates="arc_documentos_solicitudes")
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="arc_documentos_solicitudes")
    usuario_receptor_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True)
    usuario_receptor = db.relationship("Usuario", foreign_keys="ArcDocumentoSolicitud.usuario_receptor_id")
    usuario_asignado_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True)
    usuario_asignado = db.relationship("Usuario", foreign_keys="ArcDocumentoSolicitud.usuario_asignado_id")

    # Columnas
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

    def __repr__(self):
        """Representación"""
        return f"<Solicitud> {self.id}"

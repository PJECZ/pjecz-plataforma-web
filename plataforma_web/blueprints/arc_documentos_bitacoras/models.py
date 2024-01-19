"""
Archivo Documentos Bitacoras, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class ArcDocumentoBitacora(db.Model, UniversalMixin):
    """Archivo Documentos"""

    ACCIONES = OrderedDict(  # varchar(16)
        [
            ("ALTA", "Alta"),
            ("EDICION DOC", "Edición del Documento"),
            ("CORRECCION FOJAS", "Corrección de Fojas"),
            ("NO ENCONTRADO", "No Encontrado"),
            ("ENVIADO", "Enviado"),
            ("ENTREGADO", "Entregado"),
            ("ARCHIVAR", "Archivar"),
            ("ANOMALIA", "Anomalía"),
            ("ELIMINADO", "Eliminado"),
            ("RECUPERADO", "Recuperado"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "arc_documentos_bitacoras"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    arc_documento_id = db.Column(db.Integer, db.ForeignKey("arc_documentos.id"), index=True, nullable=False)
    arc_documento = db.relationship("ArcDocumento", back_populates="arc_documentos_bitacoras")
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="arc_documentos_bitacoras")

    # Columnas
    fojas = db.Column(db.Integer)
    accion = db.Column(
        db.Enum(*ACCIONES, name="tipo_accion", native_enum=False),
        nullable=False,
    )
    observaciones = db.Column(db.String(256))

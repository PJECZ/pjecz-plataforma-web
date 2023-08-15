"""
Archivo Documentos, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class ArcDocumento(db.Model, UniversalMixin):
    """Archivo Documentos"""

    UBICACIONES = OrderedDict(  # varchar(16)
        [
            ("NO DEFINIDO", "No Definido"),
            ("ARCHIVO", "Archivo"),
            ("JUZGADO", "Juzgado"),
            ("REMESA", "Remesa"),
        ]
    )

    TIPO_JUZGADOS = OrderedDict(  # varchar(16)
        [
            ("ORAL", "Oral"),
            ("TRADICIONAL", "Tradicional"),
        ]
    )

    TIPOS = OrderedDict(  # varchar(16)
        [
            ("NO DEFINIDO", "No Definido"),
            ("CUADERNILLO", "Cuadernillo"),
            ("ENCOMIENDA", "Encomienda"),
            ("EXHORTO", "Exhorto"),
            ("EXPEDIENTE", "Expediente"),
            ("EXPEDIENTILLO", "Expedientillo"),
            ("FOLIO", "Folio"),
            ("LIBRO", "Libro"),
            ("TOCA", "TOCA"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "arc_documentos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="arc_documentos")
    arc_juzgado_origen_id = db.Column(db.Integer, db.ForeignKey("arc_juzgados_extintos.id"), index=True, nullable=True)
    arc_juzgado_origen = db.relationship("ArcJuzgadoExtinto", back_populates="arc_documentos")
    arc_documento_tipo_id = db.Column(db.Integer, db.ForeignKey("arc_documentos_tipos.id"), index=True, nullable=True)
    arc_documento_tipo = db.relationship("ArcDocumentoTipo", back_populates="arc_documentos_tipos")

    # Columnas
    actor = db.Column(db.String(256), nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    demandado = db.Column(db.String(256))
    expediente = db.Column(db.String(16), index=True, nullable=False)  # dígitos/YYYY-XXX
    juicio = db.Column(db.String(128))
    fojas = db.Column(db.Integer, nullable=False)
    tipo_juzgado = db.Column(
        db.Enum(*TIPO_JUZGADOS, name="tipo_juzgados", native_enum=False),
        nullable=False,
    )
    ubicacion = db.Column(
        db.Enum(*UBICACIONES, name="ubicaciones", native_enum=False),
        nullable=False,
        default="NO DEFINIDO",
        server_default="NO DEFINIDO",
    )
    tipo = db.Column(
        db.Enum(*TIPOS, name="tipos", native_enum=False),
        index=True,
        nullable=False,
        default="NO DEFINIDO",
        server_default="NO DEFINIDO",
    )
    notas = db.Column(db.String(256))

    # Hijos
    arc_documentos_bitacoras = db.relationship("ArcDocumentoBitacora", back_populates="arc_documento", lazy="noload")
    arc_solicitudes = db.relationship("ArcSolicitud", back_populates="arc_documento", lazy="noload")
    arc_remesas_documentos = db.relationship("ArcRemesaDocumento", back_populates="arc_documento", lazy="noload")

    def __repr__(self):
        """Representación"""
        return f"<Documentos> {self.id}"

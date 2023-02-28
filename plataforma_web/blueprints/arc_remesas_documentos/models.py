"""
Archivo - Remesas Documentos, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class ArcRemesaDocumento(db.Model, UniversalMixin):
    """Archivo - Remesa"""

    TIPOS = OrderedDict(  # varchar(16)
        [
            ("TRADICIONAL", "Pendiente"),
            ("ORAL", "Cancelado"),
        ]
    )

    ANOMALIAS = OrderedDict(  # varchar(64)
        [
            ("EXPEDIENTE CON NUMERO INCORRECTO", "Expediente con número incorrecto"),
            ("EXPEDIENTE CON ANO INCORRECTO", "Expediente con año incorrecto"),
            ("EXPEDIENTE ENLISTADO Y NO ENVIADO", "Expediente enlistado y no enviado"),
            ("EXPEDIENTE CON PARTES INCORRECTAS", "Expediente con partes incorrectas"),
            ("EXPEDIENTE SIN FOLIAR", "Expediente sin foliar"),
            ("EXPEDIENTE FOLIADO INCORRECTAMENTE", "Expediente foliado incorrectamente"),
            ("EXPEDIENTE DESGLOSADO", "Expediente desglosado"),
            ("EXPEDIENTE CON CARATULA EN MAL ESTADO", "Expediente con caratula en mal estado"),
            ("EXPEDIENTE SIN CARATULA", "Expediente sin caratula"),
            ("EXPEDIENTE SIN ESPECIFICACION DE TOMOS ENVIADOS", "Expediente sin especificación de tomos enviados"),
            ("EXPEDIENTE CON CAPTURA ERRONEA DE FOJAS", "Expediente con captura errónea de fojas"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "arc_remesas_documentos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    arc_documento_id = db.Column(db.Integer, db.ForeignKey("arc_documentos.id"), index=True, nullable=False)
    arc_documento = db.relationship("ArcDocumento", back_populates="arc_remesas_documentos")
    arc_remesa_id = db.Column(db.Integer, db.ForeignKey("arc_remesas.id"), index=True)
    arc_remesa = db.relationship("ArcRemesa", back_populates="arc_remesas_documentos")

    # Columnas
    anomalia = db.Column(db.Enum(*ANOMALIAS, name="anomalias", native_enum=False))
    fojas = db.Column(db.Integer, nullable=False)
    observaciones_solicitante = db.Column(db.String(256))
    observaciones_archivista = db.Column(db.String(256))
    tipo_juzgado = db.Column(
        db.Enum(*TIPOS, name="tipos", native_enum=False),
        nullable=False,
    )

    def __repr__(self):
        """Representación"""
        return f"<Remesa Documento> {self.id}"

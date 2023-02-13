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
    tiene_anomalia = db.Column(db.Boolean, default=False)
    fojas = db.Column(db.Integer, nullable=False)
    observaciones = db.Column(db.String(256))
    tipo_juzgado = db.Column(
        db.Enum(*TIPOS, name="tipos", native_enum=False),
        nullable=False,
    )

    def __repr__(self):
        """Representación"""
        return f"<Remesa Documento> {self.id}"

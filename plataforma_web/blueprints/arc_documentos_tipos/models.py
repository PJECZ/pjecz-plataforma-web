"""
Archivo Documentos Tipos, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class ArcDocumentoTipo(db.Model, UniversalMixin):
    """Archivo Documentos Tipos"""

    # Nombre de la tabla
    __tablename__ = "arc_documentos_tipos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    nombre = db.Column(db.String(32), unique=True, nullable=False)

    # Hijos
    arc_documentos_tipos = db.relationship("ArcDocumento", back_populates="arc_documento_tipo", lazy="noload")
    arc_remesas = db.relationship("ArcRemesa", back_populates="arc_documento_tipo", lazy="noload")

    def __repr__(self):
        """Representación"""
        return f"<Tipo de Documento> {self.id}"

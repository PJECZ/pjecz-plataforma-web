"""
CID Procedimientos, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class CIDProcedimiento(db.Model, UniversalMixin):
    """CIDProcedimiento"""

    ETAPAS = OrderedDict(
        [
            ("ELABORADO", "Elaborado"),
            ("REVISADO", "Revisado"),
            ("APROBADO", "Aprobado"),
            ("ARCHIVADO", "Archivado"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "cid_procedimientos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    codigo = db.Column(db.String(16), nullable=False)
    revision = db.Column(db.Integer(), nullable=False)
    fecha = db.Column(db.Date(), nullable=False)
    # OBJETIVO
    # ALCANCE
    # DOCUMENTOS DE REFERENCIA
    # DEFINICIONES
    # RESPONSABILIDADES
    # DESARROLLO
    # CONTROL DE LOS REGISTROS
    # CONTROL DE CAMBIOS
    # elaboro
    # reviso
    # aprobo
    etapa = db.Column(
        db.Enum(*ETAPAS, name="etapas", native_enum=False),
        index=True,
        nullable=False,
    )
    contenido = db.Column(db.Text(), nullable=False)

    # Hijos
    formatos = db.relationship("CIDFormato", back_populates="procedimiento")

    def __repr__(self):
        """Representación"""
        return "<CIDProcedimiento>"

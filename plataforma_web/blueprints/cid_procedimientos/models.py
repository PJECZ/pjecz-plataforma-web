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
        ]
    )

    # Nombre de la tabla
    __tablename__ = "cid_procedimientos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    etapa = db.Column(
        db.Enum(*ETAPAS, name="etapas", native_enum=False),
        index=True,
        nullable=False,
    )
    descripcion = db.Column(db.String(256), nullable=False)
    # codigo
    # revision
    # fecha
    contenido = db.Column(db.Text(), nullable=False)
    # elaboro
    # reviso
    # aprobo

    # Hijos
    formatos = db.relationship("CIDFormato", back_populates="procedimiento")

    def __repr__(self):
        """Representación"""
        return f"<CIDProcedimiento {self.descripcion}>"

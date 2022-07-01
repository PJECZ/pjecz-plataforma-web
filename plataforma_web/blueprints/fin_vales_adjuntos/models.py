"""
Financieros Vales Adjuntos, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class FinValeAdjunto(db.Model, UniversalMixin):
    """FinValeAdjunto"""

    TIPOS = OrderedDict(
        [
            ("NO DEFINIDO", "No definido"),
            ("FACTURA PDF", "Factura PDF"),
            ("FACTURA XML", "Factura XML"),
            ("Recibo", "Recibo"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "fin_vales_adjuntos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    fin_vale_id = db.Column(db.Integer, db.ForeignKey("fin_vales.id"), index=True, nullable=False)
    fin_vale = db.relationship("FinVale", back_populates="fin_vales_adjuntos")

    # Columnas
    tipo = db.Column(
        db.Enum(*TIPOS, name="tipos", native_enum=False),
        index=True,
        nullable=False,
        default="NO DEFINIDO",
        server_default="NO DEFINIDO",
    )
    archivo = db.Column(db.String(256), nullable=False, default="", server_default="")
    url = db.Column(db.String(512), nullable=False, default="", server_default="")

    def __repr__(self):
        """Representación"""
        return f"<FinValeAdjunto {self.id}>"

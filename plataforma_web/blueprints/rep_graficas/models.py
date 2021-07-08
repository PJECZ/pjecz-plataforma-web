"""
Rep Graficas, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class RepGrafica(db.Model, UniversalMixin):
    """RepGrafica"""

    CORTES = OrderedDict(
        [
            ("NO DEFINIDO", "No Definido"),
            ("DIARIO", "Diario"),
            ("MENSUAL", "Mensual"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "rep_graficas"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    desde = db.Column(db.Date(), nullable=False)
    hasta = db.Column(db.Date(), nullable=False)
    corte = db.Column(
        db.Enum(*CORTES, name="progresos", native_enum=False),
        index=True,
        nullable=False,
    )

    # Hijos
    rep_reportes = db.relationship("RepReporte", back_populates="rep_grafica")

    def __repr__(self):
        """Representación"""
        return "<RepGrafica>"

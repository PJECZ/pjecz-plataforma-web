"""
Rep Resultados, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class RepResultado(db.Model, UniversalMixin):
    """Rep Resultado"""

    TIPOS = OrderedDict(
        [
            ("TOTAL", "No definido"),
            ("EXITOSO", "Exitoso"),
            ("ADVERTENCIA", "Advertencia"),
            ("PROBLEMATICO", "Problemático"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "rep_resultados"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    reporte_id = db.Column(db.Integer, db.ForeignKey("rep_reportes.id"), index=True, nullable=False)
    reporte = db.relationship("RepReporte", back_populates="resultados")
    modulo_id = db.Column(db.Integer, db.ForeignKey("modulos.id"), index=True, nullable=False)
    modulo = db.relationship("Modulo", back_populates="resultados")

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    tipo = db.Column(
        db.Enum(*TIPOS, name="tipos", native_enum=False),
        index=True,
        nullable=False,
    )
    cantidad = db.Column(db.Integer(), nullable=False)

    def __repr__(self):
        """Representación"""
        return "<Resultado>"

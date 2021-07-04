"""
Rep Reportes, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class RepReporte(db.Model, UniversalMixin):
    """Rep Reporte"""

    PROGRESOS = OrderedDict(
        [
            ("PENDIENTE", "Pendiente"),
            ("ELABORANDO", "Elaborando"),
            ("TERMINADO", "Terminado"),
            ("ARCHIVADO", "Archivado"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "rep_reportes"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    grafica_id = db.Column(db.Integer, db.ForeignKey("rep_graficas.id"), index=True, nullable=False)
    grafica = db.relationship("RepGrafica", back_populates="reportes")

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    desde = db.Column(db.DateTime(), nullable=False)
    hasta = db.Column(db.DateTime(), nullable=False)
    programado = db.Column(db.DateTime(), nullable=False)
    progreso = db.Column(
        db.Enum(*PROGRESOS, name="progresos", native_enum=False),
        index=True,
        nullable=False,
    )

    # Hijos
    resultados = db.relationship("RepResultado", back_populates="reporte")

    def __repr__(self):
        """Representación"""
        return "<Reporte>"

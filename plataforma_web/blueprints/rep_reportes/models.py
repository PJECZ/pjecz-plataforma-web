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
            ("NO DEFINIDO", "No Definido"),
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
    rep_grafica_id = db.Column(db.Integer, db.ForeignKey("rep_graficas.id"), index=True, nullable=False)
    rep_grafica = db.relationship("RepGrafica", back_populates="rep_reportes")

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    inicio = db.Column(db.DateTime(), nullable=False)
    termino = db.Column(db.DateTime(), nullable=False)
    programado = db.Column(db.DateTime(), nullable=False)
    progreso = db.Column(
        db.Enum(*PROGRESOS, name="progresos", native_enum=False),
        index=True,
        nullable=False,
    )

    # Hijos
    rep_resultados = db.relationship("RepResultado", back_populates="rep_reporte")

    def __repr__(self):
        """Representación"""
        return f"<Reporte {self.inicio.strftime('%Y-%m-%d')}>"

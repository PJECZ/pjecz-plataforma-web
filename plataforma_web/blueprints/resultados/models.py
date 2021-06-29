"""
Resultados, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Resultados(db.Model, UniversalMixin):
    """Resultados"""

    MODULOS = OrderedDict(
        [
            ("AUDIENCIAS", "Audiencias"),
            ("EDICTOS", "Edictos"),
            ("GLOSAS", "Glosas"),
            ("LISTAS DE ACUERDOS", "Listas de Acuerdos"),
            ("SENTENCIAS", "Sentencias"),
            ("UBICACIONES DE EXPEDIENTES", "Ubicaciones de Expedientes"),
        ]
    )
    TIPOS = OrderedDict(
        [
            ("TOTAL", "Total"),
            ("EXITOSO", "Exitoso"),
            ("ADVERTENCIA", "Advertencia"),
            ("PROBLEMATICO", "Problemático"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "resultados"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    reporte_id = db.Column(db.Integer, db.ForeignKey("reportes.id"), index=True, nullable=False)
    reporte = db.relationship("Reporte", back_populates="resultados")
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="autoridades")

    # Columnas
    modulo = db.Column(
        db.Enum(*MODULOS, name="modulos", native_enum=False),
        index=True,
        nullable=False,
    )
    tipo = db.Column(
        db.Enum(*TIPOS, name="tipos", native_enum=False),
        index=True,
        nullable=False,
    )
    cantidad = db.Column(db.Integer(), nullable=False)
    url = db.Column(db.String(512), nullable=False)

    def __repr__(self):
        """Representación"""
        return "<Resultados>"

"""
Resultados, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Resultado(db.Model, UniversalMixin):
    """Resultado"""

    TIPOS = OrderedDict(
        [
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
    modulo_id = db.Column(db.Integer, db.ForeignKey('modulos.id'), index=True, nullable=False)
    modulo = db.relationship('Modulo', back_populates='resultados')

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
        return f"<Resultado {self.descripcion}>"

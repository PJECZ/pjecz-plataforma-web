"""
Escrituras, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class NotEscritura(db.Model, UniversalMixin):
    """NotEscritura"""

    ESTADOS = OrderedDict(
        [
            ("TRABAJANDO", "Trabajando"),
            ("ENVIADO", "Enviado"),
            ("EN REVISION", "En Revision"),
            ("FINALIZADO", "Finalizado"),
        ]
    )
    # Nombre de la tabla
    __tablename__ = "not_escrituras"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="not_escrituras")

    # Columnas
    fecha = db.Column(db.Date, index=True, nullable=False)
    fecha_limite = db.Column(db.Date, index=True, nullable=False)
    notaria = db.Column(db.Integer, nullable=False)
    expediente = db.Column(db.String(16), nullable=False, default="", server_default="")
    estado = db.Column(
        db.Enum(*ESTADOS, name="not_escrituras_estados", native_enum=False),
        index=True,
        nullable=False,
    )
    contenido = db.Column(db.JSON())

    def __repr__(self):
        """Representación"""
        return "<NotEscritura>"

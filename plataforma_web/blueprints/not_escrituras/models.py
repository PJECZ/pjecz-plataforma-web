"""
not_escrituras, modelos
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
            ("APROBADO", "Aprobado"),
            ("CERRADO", "Cerrado"),
            ("CORRECCIONES", "Correccion"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "not_escrituras"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    notaria_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    notaria = db.relationship("Autoridad", foreign_keys="NotEscritura.notaria_id")
    juzgado_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    juzgado = db.relationship("Autoridad", foreign_keys="NotEscritura.juzgado_id")

    # Columnas
    estado = db.Column(
        db.Enum(*ESTADOS, name="not_escrituras_estados", native_enum=False),
        index=True,
        nullable=False,
    )
    contenido = db.Column(db.JSON())

    def __repr__(self):
        """Representación"""
        return "<NotEscritura>"

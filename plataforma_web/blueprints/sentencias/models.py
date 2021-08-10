"""
Sentencias, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Sentencia(db.Model, UniversalMixin):
    """Sentencia"""

    TIPOS_JUICIOS = OrderedDict(
        [
            ("ND", "No definido"),
            ("ORAL", "Oral"),
            ("TRADICIONAL", "Tradicional"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "sentencias"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea autoridad
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="sentencias")

    # Columnas
    sentencia = db.Column(db.String(16), index=True, nullable=False)
    sentencia_fecha = db.Column(db.Date, index=True, nullable=True)
    expediente = db.Column(db.String(16), index=True, nullable=False)
    es_paridad_genero = db.Column(db.Boolean, nullable=False, default=False)
    fecha = db.Column(db.Date, index=True, nullable=False)

    # NUEVO Clave foránea
    materia_id = db.Column(db.Integer, db.ForeignKey("materias.id"), index=True, nullable=False)
    materia = db.relationship("Materia", back_populates="sentencias")

    # NUEVO Columnas
    descripcion = db.Column(db.String(256), nullable=False, default="", server_default="")
    tipo_juicio = db.Column(
        db.Enum(*TIPOS_JUICIOS, name="tipos_juicios", native_enum=False),
        index=True,
        nullable=False,
        server_default="ND",
    )

    # Archivo
    archivo = db.Column(db.String(256))
    url = db.Column(db.String(512))

    def __repr__(self):
        """Representación"""
        return f"<Sentencia {self.archivo}>"

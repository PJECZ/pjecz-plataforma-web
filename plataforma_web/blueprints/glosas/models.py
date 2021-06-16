"""
Glosas, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Glosa(db.Model, UniversalMixin):
    """Glosa"""

    TIPOS_JUICIOS = OrderedDict(
        [
            ("ND", "No Definido"),
            ("AMPARO", "Amparo"),
            ("EJECUCION", "Ejecución"),
            ("JUICIO ORAL", "Juicio Oral"),
            ("JUICIO DE NULIDAD", "Juicio de Nulidad"),
            ("LABORAL LAUDO", "Laboral Laudo"),
            ("ORAL", "Oral"),
            ("PENAL", "Penal"),
            ("SALA CIVIL", "Sala Civil"),
            ("SALA CIVIL Y FAMILIAR", "Sala Civil y Familiar"),
            ("TRADICIONAL", "Tradicional"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "glosas"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="glosas")

    # Columnas
    fecha = db.Column(db.Date, index=True, nullable=False)
    tipo_juicio = db.Column(db.Enum(*TIPOS_JUICIOS, name="tipos_juicios", native_enum=False), index=True, nullable=False)
    descripcion = db.Column(db.String(256), nullable=False)
    expediente = db.Column(db.String(16), nullable=False)
    archivo = db.Column(db.String(256))
    url = db.Column(db.String(512))

    def __repr__(self):
        """Representación"""
        return f"<Glosa fecha {self.fecha}, tipo {self.tipo_juicio}, expediente {self.expediente}>"

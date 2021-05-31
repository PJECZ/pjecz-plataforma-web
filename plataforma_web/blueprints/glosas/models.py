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
            ("AMP", "Amparo"),
            ("AUD", "Audiencia Oral"),
            ("INC", "Cuestión de Inconstitucionalidad"),
            ("JO", "Juicio Oral"),
            ("JN", "Juicio de Nulidad"),
            ("JOC", "Juicio Ordinario Civil"),
            ("JOM", "Juicio Ordinario Mercantil"),
            ("LAB", "Laboral Laudo"),
            ("PEN", "Penal"),
            ("PD", "Procedimiento Disciplinario"),
            ("PP", "Procedimiento a Perito"),
            ("RA", "Recurso de Apelación"),
            ("RQ", "Recurso de Queja"),
            ("S", "Sala"),
            ("SCF", "Sala Civil y Familiar"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "glosas"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autoridad_id = db.Column("autoridad", db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)

    # Columnas
    fecha = db.Column(db.Date, index=True, nullable=False)
    tipo_juicio = db.Column(db.Enum(*TIPOS_JUICIOS, name="tipos_juicios", native_enum=False), index=True, nullable=False)
    descripcion = db.Column(db.String(64), nullable=False)
    expediente = db.Column(db.String(16), index=True, nullable=False)
    archivo = db.Column(db.String(256))
    url = db.Column(db.String(512))

    def __repr__(self):
        """Representación"""
        return f"<Glosa {self.archivo}>"

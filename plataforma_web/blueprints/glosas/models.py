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
            ("AMPARO", "Amparo"),
            ("AUDIENCIA ORAL", "Audiencia Oral"),
            ("CUESTION DE INCONSTITUCIONALIDAD", "Cuestión de Inconstitucionalidad"),
            ("JUICIO ORAL", "Juicio Oral"),
            ("JUICIO DE NULIDAD", "Juicio de Nulidad"),
            ("JUICIO ORDINARIO CIVIL", "Juicio Ordinario Civil"),
            ("JUICIO ORDINARIO MERCANTIL", "Juicio Ordinario Mercantil"),
            ("LABORAL LAUDO", "Laboral Laudo"),
            ("PENAL", "Penal"),
            ("PROCEDIMIENTO A PERITO", "Procedimiento a Perito"),
            ("PROCEDIMIENTO DISCIPLINARIO", "Procedimiento Disciplinario"),
            ("RECURSO DE APELACION", "Recurso de Apelación"),
            ("RECURSO DE QUEJA", "Recurso de Queja"),
            ("SALA", "Sala"),
            ("SALA COLEGIADA CIVIL Y FAMILIAR", "Sala Colegiada Civil y Familiar"),
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
    descripcion = db.Column(db.String(256), nullable=False)
    expediente = db.Column(db.String(256), nullable=False)
    archivo = db.Column(db.String(256))
    url = db.Column(db.String(512))

    def __repr__(self):
        """Representación"""
        return f"<Glosa {self.archivo}>"


class GlosaException(Exception):
    """Error por datos ilegales"""

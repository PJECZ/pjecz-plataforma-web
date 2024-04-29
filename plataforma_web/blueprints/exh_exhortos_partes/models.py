"""
Exhortos Partes Persona
"""

from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin

class ExhExhortoParte(db.Model, UniversalMixin):
    """Exhorto Parte"""

    GENEROS = OrderedDict(
        [
            ("M", "MASCULINO"),
            ("F", "FEMENINO"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "exh_exhortos_partes"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    exh_exhorto_id = db.Column(db.Integer, db.ForeignKey('exh_exhortos.id'), index=True, nullable=False)
    exh_exhorto = db.relationship('ExhExhorto', back_populates='exh_exhortos_partes')

    # Columnas
    nombre = db.Column(db.String(256), nullable=False)
    apellido_paterno = db.Column(db.String(256))
    apellido_materno = db.Column(db.String(256))
    genero = db.Column(db.Enum(*GENEROS, name="tipos_generos", native_enum=False), nullable=True)
    es_persona_moral = db.Column(db.Boolean, nullable=False)
    tipo_parte = db.Column(db.Integer(), nullable=False, default=0) # 1 = Actor, Promovente, Ofendido; 2 = Demandado, Inculpado, Imputado; 0 = No definido
    tipo_parte_nombre = db.Column(db.String(256))

    def __repr__(self):
        """Representación"""
        return f"<ExhExhortoParte {self.nombre}>"
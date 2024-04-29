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
    exh_exhorto_id = db.Column(db.Integer, db.ForeignKey("exh_exhortos.id"), index=True, nullable=False)
    exh_exhorto = db.relationship("ExhExhorto", back_populates="exh_exhortos_partes")

    # Nombre de la parte, en el caso de persona moral, solo en nombre de la empresa o razón social.
    nombre = db.Column(db.String(256), nullable=False)

    # Apellido paterno de la parte. Solo cuando no sea persona moral.
    apellido_paterno = db.Column(db.String(256))

    # Apellido materno de la parte, si es que aplica para la persona. Solo cuando no sea persona moral.
    apellido_materno = db.Column(db.String(256))

    # 'M' = Masculino,
    # 'F' = Femenino.
    # Solo cuando aplique y se quiera especificar (que se tenga el dato). NO aplica para persona moral.
    genero = db.Column(db.Enum(*GENEROS, name="tipos_generos", native_enum=False), nullable=True)

    # Valor que indica si la parte es una persona moral.
    es_persona_moral = db.Column(db.Boolean, nullable=False)

    # Indica el tipo de parte:
    # 1 = Actor, Promovente, Ofendido;
    # 2 = Demandado, Inculpado, Imputado;
    # 0 = No definido o se especifica en tipoParteNombre
    tipo_parte = db.Column(db.Integer, nullable=False, default=0)

    # Aquí se puede especificar el nombre del tipo de parte.
    tipo_parte_nombre = db.Column(db.String(256))

    def __repr__(self):
        """Representación"""
        return f"<ExhExhortoParte {self.id}>"

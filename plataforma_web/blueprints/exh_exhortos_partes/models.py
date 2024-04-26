"""
Exhortos Partes Persona
"""

from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin

class ExhParte(db.Model, UniversalMixin):
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

    # Columnas
    nombre = db.Column(db.String(256), nullable=False)
    apellidoPaterno = db.Column(db.String(256))
    apellidoMaterno = db.Column(db.String(256))
    genero = db.Column(db.Enum(*GENEROS, name="tipos_generos", native_enum=False), nullable=True)
    esPersonaMoral = db.Column(db.Boolean, nullable=False)
    tipoParte = db.Column(db.Integer(), nullable=False, default=0) # 1 = Actor, Promovente, Ofendido; 2 = Demandado, Inculpado, Imputado; 0 = No definido
    tipoParteNombre = db.Column(db.String(256))

    def __repr__(self):
        """Representación"""
        return f"<ExhParte {self.nombre}>"
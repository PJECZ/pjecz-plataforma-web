"""
Identidades Generos, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class IdentidadGenero(db.Model, UniversalMixin):
    """IdentidadGenero"""

    GENEROS = OrderedDict(
        [
            ("MASCULINO", "Masculino"),
            ("FEMENINO", "Femenino"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "identidades_generos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    nombre_anterior = db.Column(db.String(256), nullable=False)
    nombre_actual = db.Column(db.String(256), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    lugar_nacimiento = db.Column(db.String(256), nullable=True)
    genero_anterior = db.Column(db.Enum(*GENEROS, name="tipo_genero_anterior", native_enum=False), nullable=False)
    genero_actual = db.Column(db.Enum(*GENEROS, name="tipo_genero_actual", native_enum=False), nullable=False)
    nombre_padre = db.Column(db.String(256), nullable=True)
    nombre_madre = db.Column(db.String(256), nullable=True)
    procedimiento = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        """Representación"""
        return f"<IdentidadGenero {self.id}>"

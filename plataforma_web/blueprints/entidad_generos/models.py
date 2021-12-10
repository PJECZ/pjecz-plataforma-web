"""
Entidad Generos, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class EntidadGenero(db.Model, UniversalMixin):
    """EntidadGenero"""

    GENEROS = OrderedDict(
        [
            ("M", "Masculino"),
            ("F", "Femenino"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "entidad_generos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea

    # Columnas
    nombre_anterior = db.Column(db.String(256), nullable=False)
    nombre_actual = db.Column(db.String(256), nullable=False)
    fecha_nacimiento = db.Column(db.Date)
    lugar_nacimiento = db.Column(db.String(256), nullable=True)
    genero_anterior = db.Column(db.Enum(*GENEROS, name="tipo_genero_anterior", native_enum=False), nullable=False)
    genero_actual = db.Column(db.Enum(*GENEROS, name="tipo_genero_actual", native_enum=False), nullable=False)
    num_empleado = db.Column(db.Integer)
    nombre_padre = db.Column(db.String(256), nullable=True)
    nombre_madre = db.Column(db.String(256), nullable=True)
    procedimiento = db.Column(db.String(256), nullable=False)

    # Hijos

    def __repr__(self):
        """Representación"""
        return f"<EntidadGenero {self.id}>"

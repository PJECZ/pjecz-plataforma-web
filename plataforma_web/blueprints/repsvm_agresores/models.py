"""
REPSVM Agresores, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class REPSVMAgresor(db.Model, UniversalMixin):
    """REPSVMAgresor"""

    TIPOS_JUZGADOS = OrderedDict(
        [
            ("ND", "No Definido"),
            ("JUZGADO ESPECIALIZADO EN VIOLENCIA FAMILIAR", "Juzgado Especializado en Violencia Familiar"),
            ("JUZGADO DE PRIMERA INSTANCIA EN MATERIA PENAL", "Juzgado de Primera Instancia en Materia Penal"),
        ]
    )

    TIPOS_SENTENCIAS = OrderedDict(
        [
            ("ND", "No Definido"),
            ("PROCEDIMIENTO ABREVIADO", "Procedimiento Abreviado"),
            ("JUICIO ORAL", "Juicio Oral"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "repsvm_agresores"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    distrito_id = db.Column(db.Integer, db.ForeignKey("distritos.id"), index=True, nullable=False)
    distrito = db.relationship("Distrito", back_populates="repsvm_agresores")

    # Columnas
    consecutivo = db.Column(db.Integer(), nullable=False)
    delito_generico = db.Column(db.String(255), nullable=False)
    delito_especifico = db.Column(db.String(255), nullable=False)
    es_publico = db.Column(db.Boolean(), default=False, nullable=False)
    nombre = db.Column(db.String(256), nullable=False)
    numero_causa = db.Column(db.String(256), nullable=False)
    pena_impuesta = db.Column(db.String(256), nullable=False)
    observaciones = db.Column(db.Text(), nullable=True)
    sentencia_url = db.Column(db.String(512), nullable=True)
    tipo_juzgado = db.Column(db.Enum(*TIPOS_JUZGADOS, name="tipos_juzgados", native_enum=False), index=True, nullable=False)
    tipo_sentencia = db.Column(db.Enum(*TIPOS_SENTENCIAS, name="tipos_juzgados", native_enum=False), index=True, nullable=False)

    # Hijos
    repsvm_agresores_delitos = db.relationship("REPSVMAgresoresDelitos", back_populates="repsvm_agresores")

    def __repr__(self):
        """Representación"""
        return f"<REPSVMAgresor {self.id}>"

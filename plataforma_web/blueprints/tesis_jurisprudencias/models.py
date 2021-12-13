"""
Tesis y Jurisprudencias, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class TesisJurisprudencia(db.Model, UniversalMixin):
    """TesisJurisprudencia"""

    TIPOS = OrderedDict(
        [
            ("POR CONTRADICCION", "Por contradicción"),
            ("REITERACION", "reiteración"),
            ("REVALIDACION", "revalidación"),
            ("DECLARACION", "declaración"),
        ]
    )

    ESTADOS = OrderedDict(
        [
            ("INTERRUMPIR", "Interrumpir"),
            ("MODIFICAR", "Modificar"),
        ]
    )

    CLASES = OrderedDict(
        [
            ("TESIS", "Tesis"),
            ("JURISPRUDENCIA", "Jurisprudencia"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "tesis_jurisprudencias"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea Órgano jurisdiccional
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="tesis_jurisprudencias")

    # Clave foránea Época
    epoca_id = db.Column(db.Integer, db.ForeignKey("epocas.id"), index=True, nullable=False)
    epoca = db.relationship("Epoca", back_populates="tesis_jurisprudencias")

    # Clave foránea Materia
    materia_id = db.Column(db.Integer, db.ForeignKey("materias.id"), index=True, nullable=False)
    materia = db.relationship("Materia", back_populates="tesis_jurisprudencias")

    # Columnas
    titulo = db.Column(db.String(256), nullable=False, default="", server_default="")  # Título
    subtitulo = db.Column(db.String(256), nullable=False, default="", server_default="")  # Subtítulo
    tipo = db.Column(db.Enum(*TIPOS, name="tipos", native_enum=False), index=True, nullable=False)  # Tipo: Por contradicción, reiteración, revalidación o por declaración (Catálogo)
    estado = db.Column(db.Enum(*ESTADOS, name="estados", native_enum=False), index=True, nullable=False)  # Estatus: interrumpir o modificar (Catálogo)
    clave_control = db.Column(db.String(24), nullable=False, default="", server_default="")  # Clave de control (Como se indica en los lineamientos)
    clase = db.Column(db.Enum(*CLASES, name="clases", native_enum=False), index=True, nullable=False)  # Indicar si es Tesis o Jurisprudencia
    rubro = db.Column(db.String(256), nullable=False, default="", server_default="")  # Rubro
    texto = db.Column(db.Text(), nullable=False)  # Texto (En su caso archivo a subir en la plataforma)
    precedentes = db.Column(db.Text(), nullable=False)  # Precedentes que sustentan las tesis
    votacion = db.Column(db.String(256), nullable=False, default="", server_default="")  # Votación con la que fue votada (Número de votos y quienes votaron en sentido afirmativo o negativo)
    votos_particulares = db.Column(db.String(256), nullable=False, default="", server_default="")  # Votos particulares(En su caso relacionar las sentencias que fueron publicadas en el sitio oficial del Poder Judicial)
    aprobacion_fecha = db.Column(db.Date(), nullable=False)  # Fecha en la que fue aprobada (Fecha y hora)
    publicacion_tiempo = db.Column(db.DateTime(), nullable=False)  # Fecha y hora de publicación de la tesis o jurisprudencia
    aplicacion_tiempo = db.Column(db.DateTime(), nullable=False)  # Fecha y hora en la que se considera de aplicación obligatoria

    # Hijos de funcionarios
    tesis_jurisprudencias_funcionarios = db.relationship('TesisJurisprudenciaFuncionario', back_populates='tesis_jurisprudencias')

    # Hijos a Sentencias
    tesis_jurisprudencias_sentencias = db.relationship('TesisJurisprudenciaSentencia', back_populates='tesis_jurisprudencia')

    @property
    def numero_registro_digital(self):
        """Número de registro digital (Número único por registro)"""
        return self.id

    def __repr__(self):
        """Representación"""
        return "<TesisJurisprudencia>"

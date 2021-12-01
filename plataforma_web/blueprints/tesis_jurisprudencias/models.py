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

    # Clave foránea Órgano jurisdiccional (Catálogo)
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="tesis_jurisprudencias")
    # Clave foránea Materia: Civil, Familiar, Mercantil, Penal, Laboral, Adolescentes y Disciplinaria (Catálogo)
    materia_id = db.Column(db.Integer, db.ForeignKey("materias.id"), index=True, nullable=False)
    materia = db.relationship("Materia", back_populates="tesis_jurisprudencias")
    # Clave foránea Época (Catálogo)
    epoca_id = db.Column(db.Integer, db.ForeignKey('epocas.id'), index=True, nullable=False)
    epoca = db.relationship('Epoca', back_populates='tesis_jurisprudencias')

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    tipo = db.Column(db.Enum(*TIPOS, name="tipos", native_enum=False), index=True, nullable=False)  # Tipo: Por contradicción, reiteración, revalidación o por declaración (Catálogo)
    estado = db.Column(db.Enum(*ESTADOS, name="estados", native_enum=False), index=True, nullable=False)  # Estatus: interrumpir o modificar (Catálogo)
    clave_control = db.Column(db.String(256), nullable=False, unique=True, index=True)  # Clave de control (Como se indica en los lineamientos)
    clase = db.Column(db.Enum(*CLASES, name="clases", native_enum=False), index=True, nullable=False)  # Indicar si es Tesis o Jurisprudencia
    instancia = db.Column(db.String(256), nullable=False)  # Instancia
    titulo = db.Column(db.String(256), nullable=False)  # Título
    subtitulo = db.Column(db.String(256), nullable=False)  # Subtítulo
    rubro = db.Column(db.String(256), nullable=False)  # Rubro
    texto = db.Column(db.JSON())  # Texto (En su caso archivo a subir en la plataforma)
    precedentes = db.Column(db.JSON())  # Precedentes que sustentan las tesis: Medio de impugnación, el número del expediente, nombre del promovente, fecha de aprobación de la resolución, la votación y el nombre del ponente
    magistrado_ponente = db.Column(db.String(256), nullable=False)  # Magistrado ponente (Nombre del magistrado ponente)
    votacion = db.Column(db.String(256), nullable=False)  # Votación con la que fue votada (Número de votos y quienes votaron en sentido afirmativo o negativo)
    votos_particulares = = db.Column(db.String(256), nullable=False)  # Votos particulares(En su caso relacionar las sentencias que fueron publicadas en el sitio oficial del Poder Judicial)
    aprobacion_fecha = db.Column(db.Date(), nullable=False)  # Fecha en la que fue aprobada (Fecha y hora)
    publicacion_tiempo = db.Column(db.DateTime(), nullable=False)  # Fecha y hora de publicación de la tesis o jurisprudencia
    aplicacion_tiempo = db.Column(db.DateTime(), nullable=False)# Fecha y hora en la que se considera de aplicación obligatoria

    @property
    def numero_registro_digital(self):
        """Número de registro digital (Número único por registro)"""
        return self.id

    def __repr__(self):
        """Representación"""
        return "<TesisJurisprudencia>"

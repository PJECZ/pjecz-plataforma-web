"""
Tesis y Jurisprudencias, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class TesisJurisprudencia(db.Model, UniversalMixin):
    """TesisJurisprudencia"""

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

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    tipo = None  # Tipo: Por contradicción, reiteración, revalidación o por declaración (Catálogo)
    estado = None  # Estatus: interrumpir o modificar (Catálogo)
    numero_registro_digital = None  # Número de registro digital (Número único por registro)
    clave_control = None  # Clave de control (Como se indica en los lineamientos)
    clase = None  # Indicar si es Tesis o Jurisprudencia
    instancia = None  # Instancia
    # Título
    # Subtítulo
    # Rubro
    # Texto (En su caso archivo a subir en la plataforma)
    # Precedentes que sustentan las tesis: Medio de impugnación, el número del expediente, nombre del promovente, fecha de aprobación de la resolución, la votación y el nombre del ponente
    # Magistrado ponente (Nombre del magistrado ponente)
    # Fecha en la que fue aprobada (Fecha y hora)
    # Votación con la que fue votada (Número de votos y quienes votaron en sentido afirmativo o negativo)
    # Votos particulares(En su caso relacionar las sentencias que fueron publicadas en el sitio oficial del Poder Judicial)
    # Fecha y hora de publicación de la tesis o jurisprudencia
    # Fecha y hora en la que se considera de aplicación obligatoria
    # Número de epoca: Primera época, segunda época

    def __repr__(self):
        """Representación"""
        return "<TesisJurisprudencia>"

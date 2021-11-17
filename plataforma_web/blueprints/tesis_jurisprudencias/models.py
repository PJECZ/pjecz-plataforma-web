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

    # Clave foránea
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="tesis_jurisprudencias")
    # Clave foránea
    materia_id = db.Column(db.Integer, db.ForeignKey("materias.id"), index=True, nullable=False)
    materia = db.relationship("Materia", back_populates="tesis_jurisprudencias")

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    tipo = None  # Por contradicción, reiteración, revalidación, por declaración
    estado = None  # Interrumpir, Modificar
    numero_registro_digital = None
    clave_control = None
    clase = None  # Tesis o Jurisprudencia
    instancia = None

    def __repr__(self):
        """Representación"""
        return "<TesisJurisprudencia>"

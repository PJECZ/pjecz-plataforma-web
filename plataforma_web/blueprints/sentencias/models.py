"""
Sentencias, modelos
"""
from urllib.parse import quote

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Sentencia(db.Model, UniversalMixin):
    """Sentencia"""

    # Nombre de la tabla
    __tablename__ = "sentencias"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="sentencias")
    materia_tipo_juicio_id = db.Column(db.Integer, db.ForeignKey("materias_tipos_juicios.id"), index=True, nullable=False)
    materia_tipo_juicio = db.relationship("MateriaTipoJuicio", back_populates="sentencias")

    # Columnas
    sentencia = db.Column(db.String(16), nullable=False)
    sentencia_fecha = db.Column(db.Date, index=True, nullable=True)
    expediente = db.Column(db.String(16), nullable=False)
    expediente_anio = db.Column(db.Integer)
    expediente_num = db.Column(db.Integer)
    fecha = db.Column(db.Date, index=True, nullable=False)
    descripcion = db.Column(db.String(1024), nullable=False, default="", server_default="")
    es_perspectiva_genero = db.Column(db.Boolean, nullable=False, default=False)
    archivo = db.Column(db.String(256), nullable=False, default="", server_default="")
    url = db.Column(db.String(512), nullable=False, default="", server_default="")

    # Hijos
    tesis_jurisprudencias_sentencias = db.relationship("TesisJurisprudenciaSentencia", back_populates="sentencia")

    @property
    def descargar_url(self):
        """URL para descargar el archivo desde el sitio web"""
        if self.id:
            return f"https://www.pjecz.gob.mx/consultas/sentencias/descargar/?id={self.id}"
        return ""

    def __repr__(self):
        """Representación"""
        return f"<Sentencia {self.archivo}>"

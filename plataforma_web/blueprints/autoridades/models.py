"""
Autoridades, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Autoridad(db.Model, UniversalMixin):
    """Autoridad"""

    ORGANOS_JURISDICCIONALES = OrderedDict(
        [
            ("NO DEFINIDO", "No Definido"),
            ("JUZGADO DE PRIMERA INSTANCIA", "Juzgado de Primera Instancia"),
            ("PLENO O SALA DEL TSJ", "Pleno o Sala del TSJ"),
            ("TRIBUNAL DISTRITAL", "Tribunal Distrital"),
            ("TRIBUNAL DE CONCILIACION Y ARBITRAJE", "Tribunal de Conciliación y Arbitraje"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "autoridades"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    distrito_id = db.Column(db.Integer, db.ForeignKey("distritos.id"), index=True, nullable=False)
    distrito = db.relationship("Distrito", back_populates="autoridades")
    materia_id = db.Column(db.Integer, db.ForeignKey("materias.id"), index=True, nullable=False)
    materia = db.relationship("Materia", back_populates="autoridades")

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    clave = db.Column(db.String(16), nullable=False, unique=True)
    es_jurisdiccional = db.Column(db.Boolean, nullable=False, default=False)
    es_notaria = db.Column(db.Boolean, nullable=False, default=False)
    organo_jurisdiccional = db.Column(
        db.Enum(*ORGANOS_JURISDICCIONALES, name="tipos_organos_jurisdiccionales", native_enum=False),
        index=True,
        nullable=False,
    )
    directorio_edictos = db.Column(db.String(256), nullable=False, default="", server_default="")
    directorio_glosas = db.Column(db.String(256), nullable=False, default="", server_default="")
    directorio_listas_de_acuerdos = db.Column(db.String(256), nullable=False, default="", server_default="")
    directorio_sentencias = db.Column(db.String(256), nullable=False, default="", server_default="")

    # Hijos
    edictos = db.relationship("Edicto", back_populates="autoridad", lazy="noload")
    glosas = db.relationship("Glosa", back_populates="autoridad", lazy="noload")
    listas_de_acuerdos = db.relationship("ListaDeAcuerdo", back_populates="autoridad", lazy="noload")
    sentencias = db.relationship("Sentencia", back_populates="autoridad", lazy="noload")
    transcripciones = db.relationship("Transcripcion", back_populates="autoridad", lazy="noload")
    ubicaciones_expedientes = db.relationship("UbicacionExpediente", back_populates="autoridad", lazy="noload")
    usuarios = db.relationship("Usuario", back_populates="autoridad")

    def __repr__(self):
        """Representación"""
        return f"<Autoridad {self.descripcion}>"

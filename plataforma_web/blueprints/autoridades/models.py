"""
Autoridades, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Autoridad(db.Model, UniversalMixin):
    """Autoridad"""

    # Nombre de la tabla
    __tablename__ = "autoridades"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    distrito_id = db.Column("distrito", db.Integer, db.ForeignKey("distritos.id"), index=True, nullable=False)

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    clave = db.Column(db.String(16), nullable=False, unique=True)
    es_jurisdiccional = db.Column(db.Boolean, nullable=False, default=False)
    es_notaria = db.Column(db.Boolean, nullable=False, default=False)
    directorio_edictos = db.Column(db.String(256), default="")
    directorio_glosas = db.Column(db.String(256), default="")
    directorio_listas_de_acuerdos = db.Column(db.String(256), default="")
    directorio_sentencias = db.Column(db.String(256), default="")

    # Hijos
    edictos = db.relationship("Edicto", backref="autoridad", lazy="noload")
    glosas = db.relationship("Glosa", backref="autoridad", lazy="noload")
    listas_de_acuerdos = db.relationship("ListaDeAcuerdo", backref="autoridad", lazy="noload")
    sentencias = db.relationship("Sentencia", backref="autoridad", lazy="noload")
    ubicaciones_expedientes = db.relationship("UbicacionExpediente", backref="autoridad", lazy="noload")
    usuarios = db.relationship("Usuario", backref="autoridad")

    def __repr__(self):
        """Representación"""
        return f"<Autoridad {self.descripcion}>"

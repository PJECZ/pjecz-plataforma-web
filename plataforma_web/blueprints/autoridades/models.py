"""
Autoridades, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Autoridad(db.Model, UniversalMixin):
    """ Autoridad """

    # Nombre de la tabla
    __tablename__ = "autoridades"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    distrito_id = db.Column("distrito", db.Integer, db.ForeignKey("distritos.id"), index=True, nullable=False)

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    clave = db.Column(db.String(16), nullable=True, unique=True)
    es_jurisdiccional = db.Column(db.Boolean, nullable=False, default=False)
    directorio_listas_de_acuerdos = db.Column(db.String(256))
    directorio_sentencias = db.Column(db.String(256))

    # Hijos
    glosas = db.relationship("Glosa", backref="autoridad", lazy="noload")
    listas_de_acuerdos = db.relationship("ListaDeAcuerdo", backref="autoridad", lazy="noload")
    ubicaciones_expedientes = db.relationship("UbicacionExpediente", backref="autoridad", lazy="noload")
    usuarios = db.relationship("Usuario", backref="autoridad")

    def __repr__(self):
        """ Representación """
        return f"<Autoridad {self.descripcion}>"

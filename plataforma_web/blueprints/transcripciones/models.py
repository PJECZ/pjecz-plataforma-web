"""
Transcripciones, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Transcripcion(db.Model, UniversalMixin):
    """ Transcripción """

    # Nombre de la tabla
    __tablename__ = "transcripciones"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autoridad_id = db.Column("autoridad", db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    expediente = db.Column(db.String(24))
    audio_url = db.Column(db.String(256))
    transcripcion = db.Column(db.Text())

    def __repr__(self):
        """ Representación """
        return f"<Transcripcion {self.nombre}>"

"""
Tesis Jurisprudencias Sentencias, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class TesisJurisprudenciaSentencia(db.Model, UniversalMixin):
    """TesisJurisprudenciaSentencia"""

    # Nombre de la tabla
    __tablename__ = "tesis_jurisprudencias_sentencias"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    tesis_jurisprudencia_id = db.Column(db.Integer, db.ForeignKey("tesis_jurisprudencias.id"), index=True, nullable=False)
    tesis_jurisprudencia = db.relationship("TesisJurisprudencia", back_populates="tesis_jurisprudencias_sentencias")

    # Clave foránea
    sentencia_id = db.Column(db.Integer, db.ForeignKey("sentencias.id"), index=True, nullable=False)
    sentencia = db.relationship("Sentencia", back_populates="tesis_jurisprudencias_sentencias")

    def __repr__(self):
        """Representación"""
        return "<TesisJurisprudenciaSentencia>"

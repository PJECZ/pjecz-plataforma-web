"""
Municipios, modelos
"""

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Municipio(db.Model, UniversalMixin):
    """Municipio"""

    # Nombre de la tabla
    __tablename__ = "municipios"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    estado_id = db.Column(db.Integer, db.ForeignKey("estados.id"), index=True, nullable=False)
    estado = db.relationship("Estado", back_populates="municipios")

    # Columnas
    clave = db.Column(db.String(3), nullable=False)
    nombre = db.Column(db.String(256), nullable=False)

    # Hijos
    # exh_exhortos_destinos = db.relationship('ExhExhorto', back_populates='municipio_destino', lazy='noload')
    exh_exhortos_origenes = db.relationship("ExhExhorto", back_populates="municipio_origen")

    def __repr__(self):
        """Representación"""
        return f"<Municipio {self.clave}>"

"""
CID Areas, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class CIDArea(db.Model, UniversalMixin):
    """CIDArea"""

    # Nombre de la tabla
    __tablename__ = "cid_areas"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    clave = db.Column(db.String(16), nullable=False, unique=True)
    nombre = db.Column(db.String(256), nullable=False)

    # Hijos
    cid_areas_autoridades = db.relationship("CIDAreaAutoridad", back_populates="cid_area")
    cid_procedimientos = db.relationship('CIDProcedimiento', back_populates='cid_area')
    cid_formatos = db.relationship('CIDFormato', back_populates='cid_area')

    def __repr__(self):
        """Representación"""
        return f"<CIDArea {self.clave}>"

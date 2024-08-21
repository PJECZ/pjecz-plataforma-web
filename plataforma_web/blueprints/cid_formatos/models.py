"""
CID Formatos, modelos
"""

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class CIDFormato(db.Model, UniversalMixin):
    """CIDFormato"""

    # Nombre de la tabla
    __tablename__ = "cid_formatos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    procedimiento_id = db.Column(db.Integer, db.ForeignKey("cid_procedimientos.id"), index=True, nullable=False)
    procedimiento = db.relationship("CIDProcedimiento", back_populates="formatos")
    cid_area_id = db.Column(db.Integer, db.ForeignKey("cid_areas.id"), index=True, nullable=False)
    cid_area = db.relationship("CIDArea", back_populates="cid_formatos")

    # Columnas
    codigo = db.Column(db.String(16), nullable=False)
    descripcion = db.Column(db.String(256), nullable=False)
    archivo = db.Column(db.String(256), nullable=False, default="", server_default="")
    url = db.Column(db.String(512), nullable=False, default="", server_default="")

    # Hijos
    registros = db.relationship("CIDRegistro", back_populates="formato")

    def __repr__(self):
        """Representación"""
        return "<CIDFormato>"

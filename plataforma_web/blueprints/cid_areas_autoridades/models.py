"""
CID Areas Autoridades, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class CIDAreaAutoridad(db.Model, UniversalMixin):
    """CIDAreaAutoridad"""

    # Nombre de la tabla
    __tablename__ = "cid_areas_autoridades"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="cid_areas_autoridades")
    cid_area_id = db.Column(db.Integer, db.ForeignKey("cid_areas.id"), index=True, nullable=False)
    cid_area = db.relationship("CIDArea", back_populates="cid_areas_autoridades")

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)

    # Hijos

    def __repr__(self):
        """Representación"""
        return f"<CIDAreaAutoridad {self.descripcion}>"

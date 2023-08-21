"""
Archivo Juzgados Extintos, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class ArcJuzgadoExtinto(db.Model, UniversalMixin):
    """Archivo Juzgado Extinto"""

    # Nombre de la tabla
    __tablename__ = "arc_juzgados_extintos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    distrito_id = db.Column(db.Integer, db.ForeignKey("distritos.id"), index=True, nullable=False)
    distrito = db.relationship("Distrito", back_populates="arc_juzgados_extintos")

    # Columnas
    clave = db.Column(db.String(16), nullable=False, unique=True)
    descripcion_corta = db.Column(db.String(64), nullable=False)
    descripcion = db.Column(db.String(256), nullable=False)

    # Hijos
    arc_documentos = db.relationship("ArcDocumento", back_populates="arc_juzgado_origen", lazy="noload")

    @property
    def nombre(self):
        """Junta clave : descripcion_corta"""
        return self.clave + " : " + self.descripcion_corta

    def __repr__(self):
        """Representación"""
        return f"<Juzgado-Extinto> {self.id}"

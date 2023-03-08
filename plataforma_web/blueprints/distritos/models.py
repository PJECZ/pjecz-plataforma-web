"""
Distritos, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Distrito(db.Model, UniversalMixin):
    """Distrito"""

    # Nombre de la tabla
    __tablename__ = "distritos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    clave = db.Column(db.String(16), nullable=False, unique=True)
    nombre = db.Column(db.String(256), unique=True, nullable=False)
    nombre_corto = db.Column(db.String(64), nullable=False, default="", server_default="")
    es_distrito_judicial = db.Column(db.Boolean, nullable=False, default=False)
    es_distrito = db.Column(db.Boolean, nullable=False, default=False)
    es_jurisdiccional = db.Column(db.Boolean, nullable=False, default=False)

    # Hijos
    autoridades = db.relationship("Autoridad", back_populates="distrito")
    centros_trabajos = db.relationship("CentroTrabajo", back_populates="distrito", lazy="noload")
    peritos = db.relationship("Perito", back_populates="distrito", lazy="noload")
    oficinas = db.relationship("Oficina", back_populates="distrito", lazy="noload")
    repsvm_agresores = db.relationship("REPSVMAgresor", back_populates="distrito", lazy="noload")

    def __repr__(self):
        """Representación"""
        return f"<Distrito {self.nombre}>"

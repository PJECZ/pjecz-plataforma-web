"""
Centros de Trabajos, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class CentroTrabajo(db.Model, UniversalMixin):
    """CentroTrabajo"""

    # Nombre de la tabla
    __tablename__ = "centros_trabajos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    distrito_id = db.Column(db.Integer, db.ForeignKey("distritos.id"), index=True, nullable=False)
    distrito = db.relationship("Distrito", back_populates="centros_trabajos")
    domicilio_id = db.Column(db.Integer, db.ForeignKey('domicilios.id'), index=True, nullable=False)
    domicilio = db.relationship('Domicilio', back_populates='centros_trabajos')

    # Columnas
    clave = db.Column(db.String(16), unique=True, nullable=False)
    nombre = db.Column(db.String(256), nullable=False)
    telefono = db.Column(db.String(48), nullable=False, default="", server_default="")
    domicilio_completo = db.Column(db.String(1024), nullable=False, default="", server_default="")

    # Hijos
    funcionarios = db.relationship("Funcionario", back_populates="centro_trabajo", lazy="noload")

    def __repr__(self):
        """Representación"""
        return f"<CentroTrabajo {self.clave}>"

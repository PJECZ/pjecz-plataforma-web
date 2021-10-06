"""
Roles, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Rol(db.Model, UniversalMixin):
    """Rol"""

    # Nombre de la tabla
    __tablename__ = "roles"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    nombre = db.Column(db.String(256), unique=True, nullable=False)

    # Hijos
    permisos = db.relationship('Permiso', back_populates='rol')
    usuarios_roles = db.relationship("UsuarioRol", back_populates="rol")

    def __repr__(self):
        """Representación"""
        return f"<Rol {self.nombre}>"

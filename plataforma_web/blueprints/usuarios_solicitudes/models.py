"""
Usuarios Solicitudes, modelos

Solicitudes de actualizaciones de los datos personales de los usuarios
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class UsuarioSolicitud(db.Model, UniversalMixin):
    """UsuarioSolicitud"""

    # Nombre de la tabla
    __tablename__ = "tabla"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="usuarios_solicitudes")

    # Columnas
    personal_email = db.Column(db.String(256), nullable=False)  # email personal en Google o Microsoft, diferente al de usuarios
    telefono_celular = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        """Representación"""
        return "<Clase>"

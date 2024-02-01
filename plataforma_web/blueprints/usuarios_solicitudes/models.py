"""
Usuarios Solicitudes, modelos

Solicitudes de actualizaciones de los datos personales de los usuarios
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class UsuarioSolicitud(db.Model, UniversalMixin):
    """UsuarioSolicitud"""

    # Nombre de la tabla
    __tablename__ = "usuarios_solicitudes"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="usuarios_solicitudes")

    # Columnas
    email_personal = db.Column(db.String(64), nullable=True)
    telefono_celular = db.Column(db.String(16), nullable=True)
    token_email = db.Column(db.String(6))
    token_telefono_celular = db.Column(db.String(6))
    validacion_email = db.Column(db.Boolean, default=False)
    validacion_telefono_celular = db.Column(db.Boolean, default=False)
    intentos_email = db.Column(db.Integer)
    intentos_telefono_celular = db.Column(db.Integer)

    def __repr__(self):
        """Representación"""
        return "<UsuariosSolicitud> {id}"

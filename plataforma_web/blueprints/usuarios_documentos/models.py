"""
Usuario Documentos, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class UsuarioDocumento(db.Model, UniversalMixin):
    """UsuarioDocumento"""

    # Nombre de la tabla
    __tablename__ = "usuarios_documentos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    url = db.Column(db.String(512), nullable=False, default="", server_default="")

    def __repr__(self):
        """Representación"""
        return f"<UsuarioDocumento {self.id}>"

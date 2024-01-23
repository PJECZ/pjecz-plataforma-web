"""
Usuarios_Nominas, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class UsuarioNomina(db.Model, UniversalMixin):
    """UsuarioNomina"""

    # Nombre de la tabla
    __tablename__ = "usuarios_nominas"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="usuarios_nominas")

    # Columnas
    fecha_quincena = db.Column(db.Date, nullable=False)
    descripcion = db.Column(db.String(64), nullable=False)
    archivo_pdf = db.Column(db.String(256), nullable=False)
    url_pdf = db.Column(db.String(64), nullable=False)
    archivo_xml = db.Column(db.String(64), nullable=False)
    url_xml = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        """Representación"""
        return "<UsuarioNomina> {id}"

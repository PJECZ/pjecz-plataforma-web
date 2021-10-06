"""
Bitácoras, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Bitacora(db.Model, UniversalMixin):
    """Bitacora"""

    # Nombre de la tabla
    __tablename__ = "bitacoras"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    modulo_id = db.Column(db.Integer, db.ForeignKey("modulos.id"), index=True, nullable=False)
    modulo = db.relationship("Modulo", back_populates="bitacoras")
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="bitacoras")

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    url = db.Column(db.String(512), nullable=False, default="", server_default="")

    def __repr__(self):
        """Representación"""
        return f"<Bitacora {self.creado} {self.descripcion}>"

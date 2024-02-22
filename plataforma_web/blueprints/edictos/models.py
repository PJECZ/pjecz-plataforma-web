"""
Edictos, modelos
"""

from urllib.parse import quote

from lib.universal_mixin import UniversalMixin
from plataforma_web.extensions import db


class Edicto(db.Model, UniversalMixin):
    """Edicto"""

    # Nombre de la tabla
    __tablename__ = "edictos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="edictos")

    # Columnas
    fecha = db.Column(db.Date, index=True, nullable=False)
    descripcion = db.Column(db.String(256), nullable=False)
    expediente = db.Column(db.String(16), nullable=False, default="", server_default="")
    numero_publicacion = db.Column(db.String(16), nullable=False, default="", server_default="")
    archivo = db.Column(db.String(256), nullable=False, default="", server_default="")
    url = db.Column(db.String(512), nullable=False, default="", server_default="")

    # Columnas nuevas
    acuse_num = db.Column(db.Integer, nullable=False, default=0)
    edicto_id_original = db.Column(db.Integer, nullable=False, default=0)

    # Hijos
    edictos_acuses = db.relationship("EdictoAcuse", back_populates="edicto")

    @property
    def descargar_url(self):
        """URL para descargar el archivo desde el sitio web"""
        if self.id:
            return f"https://www.pjecz.gob.mx/consultas/edictos/descargar/?id={self.id}"
        return ""

    def __repr__(self):
        """Representación"""
        return f"<Edicto {self.descripcion}>"

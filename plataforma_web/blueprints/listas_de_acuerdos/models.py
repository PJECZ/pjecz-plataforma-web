"""
Listas de Acuerdos, modelos
"""
from plataforma_web.extensions import db
from urllib.parse import quote

from lib.universal_mixin import UniversalMixin


class ListaDeAcuerdo(db.Model, UniversalMixin):
    """ListaDeAcuerdo"""

    # Nombre de la tabla
    __tablename__ = "listas_de_acuerdos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="listas_de_acuerdos")

    # Columnas
    fecha = db.Column(db.Date, index=True, nullable=False)
    descripcion = db.Column(db.String(256), nullable=False)
    archivo = db.Column(db.String(256), nullable=False, default="", server_default="")
    url = db.Column(db.String(512), nullable=False, default="", server_default="")

    # Hijos
    listas_de_acuerdos_acuerdos = db.relationship("ListaDeAcuerdoAcuerdo", back_populates="lista_de_acuerdo")

    @property
    def descargar_url(self):
        """URL para descargar el archivo desde Google Cloud Storage"""
        return f"/listas_de_acuerdos/descargar?url={quote(self.url)}"

    def __repr__(self):
        """Representación"""
        return f"<ListaDeAcuerdo {self.archivo}>"

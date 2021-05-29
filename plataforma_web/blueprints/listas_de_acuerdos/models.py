"""
Listas de Acuerdos, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class ListaDeAcuerdo(db.Model, UniversalMixin):
    """ListaDeAcuerdo"""

    # Nombre de la tabla
    __tablename__ = "listas_de_acuerdos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autoridad_id = db.Column("autoridad", db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)

    # Columnas
    fecha = db.Column(db.Date, index=True, nullable=False)
    descripcion = db.Column(db.String(256), nullable=False)
    archivo = db.Column(db.String(256))
    url = db.Column(db.String(512))

    def __repr__(self):
        """Representación"""
        return f"<ListaDeAcuerdo {self.archivo}>"

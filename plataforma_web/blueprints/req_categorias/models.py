"""
Requisiciones Categorias, modelos
"""

import inspect
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class ReqCategoria(db.Model, UniversalMixin):
    """ReqCategoria"""

    # Nombre de la tabla
    __tablename__ = "req_categorias"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)

    # Hijos
    req_catalogos = db.relationship("ReqCatalogo", back_populates="req_categoria")

    def __repr__(self):
        """Representación"""
        return f"<ReqCategoria {self.id}>"

    def object_as_dict(obj):
        return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

"""
Requisiciones Catalogos, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin
from sqlalchemy import inspect


class ReqCatalogo(db.Model, UniversalMixin):
    """ReqCatalogo"""

    # Nombre de la tabla
    __tablename__ = "req_catalogos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    codigo = db.Column(db.String(3), nullable=False, unique=True)
    descripcion = db.Column(db.String(256), nullable=False)
    unidad_medida = db.Column(db.String(50), nullable=False)

    # Hijos
    req_requisiciones_registros = db.relationship("ReqRequisicionRegistro", back_populates="req_catalogo")

    def __repr__(self):
        """Representación"""
        return f"<ReqCatalogo {self.codigo}>"

    def object_as_dict(obj):
        return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

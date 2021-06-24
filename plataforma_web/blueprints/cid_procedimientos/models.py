"""
CID Procedimientos, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class CIDProcedimiento(db.Model, UniversalMixin):
    """ CIDProcedimiento """

    # Nombre de la tabla
    __tablename__ = "cid_procedimientos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    contenido = db.Column(db.Text(), nullable=False)

    # Hijos
    formatos = db.relationship('CIDFormato', back_populates='procedimiento')

    def __repr__(self):
        """ Representación """
        return f"<CIDProcedimiento {self.descripcion}>"

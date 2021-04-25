"""
CID Formatos, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class CIDFormato(db.Model, UniversalMixin):
    """ CIDFormato """

    # Nombre de la tabla
    __tablename__ = "cid_formatos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    procedimiento_id = db.Column("procedimiento", db.Integer, db.ForeignKey("cid_procedimientos.id"), index=True, nullable=False)

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)

    # Hijos
    registros = db.relationship("CIDRegistro", backref="formato")

    def __repr__(self):
        """ Representación """
        return f"<CIDFormato {self.descripcion}>"

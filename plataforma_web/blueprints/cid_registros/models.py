"""
Registros, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class CIDRegistro(db.Model, UniversalMixin):
    """ CIDRegistro """

    # Nombre de la tabla
    __tablename__ = "cid_registros"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    formato_id = db.Column("formato", db.Integer, db.ForeignKey("cid_formatos.id"), index=True, nullable=False)

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        """ Representación """
        return f"<CIDRegistro {self.descripcion}>"

"""
Requisiciones registros, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class ReqRequisicionRegistro(db.Model, UniversalMixin):
    """ ReqRequisionRegistro """

    # Nombre de la tabla
    __tablename__ = 'req_requisiciones_registros'

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    req_catalogo_id = db.Column(db.Integer, db.ForeignKey("req_catalogos.id"), index=True, nullable=False)
    req_catalogo = db.relationship("ReqCatalogo", back_populates="req_requisiciones_registros")

    req_requisicion_id = db.Column(db.Integer , db.ForeignKey("req_requisiciones.id"), index=True , nullable = False)
    req_requisicion = db.relationship("ReqRequisicion" , back_populates="req_requisiciones_registros")

    # Columnas
    cantidad = db.Column(db.Integer, nullable=False)    

    def __repr__(self):
        """ Representación """
        return '<ReqRequisionRegistro>'

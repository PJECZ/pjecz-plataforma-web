"""
Requisiciones , modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class ReqRequisicion(db.Model, UniversalMixin):
    """ ReqRequision """

    # Nombre de la tabla
    __tablename__ = 'req_requisiciones'

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    fecha = db.Column(db.DateTime , nullable=False)
    consecutivo = db.Column(db.String(30) , nullable=False)
    autoridad_id = db.Column(db.Integer, nullable=False)
    observaciones = db.Column(db.Text())
    usuario_id = db.Column(db.Integer)
    revisa_id = db.Column(db.Integer)
    autoriza_id = db.Column(db.Integer)
    entrega_id = db.Column(db.Integer)
    estado = db.Column(db.String(30) , nullable=False)

    # Hijos
    # req_resguardos
    req_resguardos = db.relationship("ReqResguardo", back_populates="req_requisicion")

    # req_requisiciones_registros
    req_requisiciones_registros = db.relationship("ReqRequisicionRegistro", back_populates="req_requisicion")

    def __repr__(self):
        """ Representación """
        return '<ReqRequision>'

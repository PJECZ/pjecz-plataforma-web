"""
Requisiciones Resguardos, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class ReqResguardo(db.Model, UniversalMixin):
    """ ReqResguardo """

    # Nombre de la tabla
    __tablename__ = 'req_resguardos'

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    archivo = db.Column(db.String(256), nullable=False)

    # Llave foranea
    req_requisicion_id = db.Column(db.Integer, db.ForeignKey("req_requisiciones.id"), index=True, nullable=False)
    req_requisicion = db.relationship("ReqRequisicion", back_populates="req_resguardos")
    

    def __repr__(self):
        """ Representación """
        return f"<ReqResguardo {self.id}>"



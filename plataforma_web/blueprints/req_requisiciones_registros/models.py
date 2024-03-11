"""
Requisiciones registros, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class ReqRequisicionRegistro(db.Model, UniversalMixin):
    """ReqRequisionRegistro"""

    CLAVES = OrderedDict(
        [
            ("INS", "INSUFICIENCIA"),
            ("REP", "REPOSICION DE BIENES"),
            ("OBS", "OBSOLESENCIA"),
            ("AMP", "AMPLIACION COBERTURA DEL SERVICIO"),
            ("NUE", "NUEVO PROYECTO"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "req_requisiciones_registros"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    req_catalogo_id = db.Column(db.Integer, db.ForeignKey("req_catalogos.id"), index=True, nullable=False)
    req_catalogo = db.relationship("ReqCatalogo", back_populates="req_requisiciones_registros")
    req_requisicion_id = db.Column(db.Integer, db.ForeignKey("req_requisiciones.id"), index=True, nullable=False)
    req_requisicion = db.relationship("ReqRequisicion", back_populates="req_requisiciones_registros")

    # Columnas
    cantidad = db.Column(db.Integer, nullable=False)
    clave = db.Column(
        db.Enum(*CLAVES, name="claves", native_enum=False),
        index=True,
        nullable=False,
    )
    detalle = db.Column(db.String)

    def __repr__(self):
        """Representación"""
        return "<ReqRequisionRegistro>"

"""
Estadisticas Acuerdos, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class EstAcuerdo(db.Model, UniversalMixin):
    """EstAcuerdo"""

    ESTADOS = OrderedDict(
        [
            ("CANCELADO", "CANCELADO"),
            ("INICIADO", "INICIADO"),
            ("TERMINADO", "TERMINADO"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "est_acuerdos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    distrito_nombre = db.Column(db.String(256), nullable=False)
    autoridad_descripcion = db.Column(db.String(256), nullable=False)
    folio = db.Column(db.String(256), nullable=False)
    expediente = db.Column(db.String(256))
    numero_caso = db.Column(db.String(256))
    fecha_elaboracion = db.Column(db.DateTime())
    fecha_validacion = db.Column(db.DateTime())
    fecha_autorizacion = db.Column(db.DateTime())
    estado = db.Column(db.Enum(*ESTADOS, name="acuerdos_estados", native_enum=False), index=True, nullable=False)
    secretario = db.Column(db.String(256))
    juez = db.Column(db.String(256))

    def __repr__(self):
        """Representación"""
        return "<EstAcuerdo>"

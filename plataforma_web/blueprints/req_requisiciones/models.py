"""
Requisiciones , modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class ReqRequisicion(db.Model, UniversalMixin):
    """ReqRequision"""

    ESTADOS = OrderedDict(
        [
            ("SOLICITADO", "Solicitado"),
            ("AUTORIZADO", "Autorizado"),
            ("REVISADO", "Revisado"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "req_requisiciones"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="req_requisiciones")

    # Columnas
    fecha = db.Column(db.DateTime, nullable=False)
    consecutivo = db.Column(db.String(30), nullable=False)
    autoridad_id = db.Column(db.Integer, nullable=False)
    observaciones = db.Column(db.Text())
    solicita_id = db.Column(db.Integer, nullable=False)
    autoriza_id = db.Column(db.Integer)
    revisa_id = db.Column(db.Integer)
    entrega_id = db.Column(db.Integer)
    estado = db.Column(
        db.Enum(*ESTADOS, name="estados", native_enum=False),
        index=True,
        nullable=False,
        default="SOLICITADO",
        server_default="SOLICITADO",
    )

    estado = db.Column(db.String(30), nullable=False)

    # Columnas estado SOLICITADO
    solicito_nombre = db.Column(db.String(256))
    solicito_puesto = db.Column(db.String(256))
    solicito_email = db.Column(db.String(256))
    solicito_efirma_tiempo = db.Column(db.DateTime)
    solicito_efirma_folio = db.Column(db.Integer)
    solicito_efirma_sello_digital = db.Column(db.String(512))
    solicito_efirma_url = db.Column(db.String(256))
    solicito_efirma_qr_url = db.Column(db.String(256))
    solicito_efirma_mensaje = db.Column(db.String(512))
    solicito_efirma_error = db.Column(db.String(512))

    # Columnas estado CANCELADO POR SOLICITANTE
    solicito_cancelo_tiempo = db.Column(db.DateTime)
    solicito_cancelo_motivo = db.Column(db.String(256))
    solicito_cancelo_error = db.Column(db.String(512))

    # Columnas estado AUTORIZADO
    autorizo_nombre = db.Column(db.String(256))
    autorizo_puesto = db.Column(db.String(256))
    autorizo_email = db.Column(db.String(256))
    autorizo_efirma_tiempo = db.Column(db.DateTime)
    autorizo_efirma_folio = db.Column(db.Integer)
    autorizo_efirma_sello_digital = db.Column(db.String(512))
    autorizo_efirma_url = db.Column(db.String(256))
    autorizo_efirma_qr_url = db.Column(db.String(256))
    autorizo_efirma_mensaje = db.Column(db.String(512))
    autorizo_efirma_error = db.Column(db.String(512))

    # Columnas estado CANCELADO POR AUTORIZANTE
    autorizo_cancelo_tiempo = db.Column(db.DateTime)
    autorizo_cancelo_motivo = db.Column(db.String(256))
    autorizo_cancelo_error = db.Column(db.String(512))

    # Columnas (step 3 authorize) estado AUTORIZADO
    reviso_nombre = db.Column(db.String(256))
    reviso_puesto = db.Column(db.String(256))
    reviso_email = db.Column(db.String(256))
    reviso_efirma_tiempo = db.Column(db.DateTime)
    reviso_efirma_folio = db.Column(db.Integer)
    reviso_efirma_sello_digital = db.Column(db.String(512))
    reviso_efirma_url = db.Column(db.String(256))
    reviso_efirma_qr_url = db.Column(db.String(256))
    reviso_efirma_mensaje = db.Column(db.String(512))
    reviso_efirma_error = db.Column(db.String(512))

    # Hijos
    req_resguardos = db.relationship("ReqResguardo", back_populates="req_requisicion")
    req_requisiciones_registros = db.relationship("ReqRequisicionRegistro", back_populates="req_requisicion")

    def __repr__(self):
        """Representación"""
        return "<ReqRequision>"

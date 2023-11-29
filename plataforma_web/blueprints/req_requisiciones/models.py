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
            ("CREADO", "Creado"),  # PASO 1
            ("SOLICITADO", "Solicitado"),  # PASO 2
            ("CANCELADO POR SOLICITANTE", "Cancelado por solicitante"),  #
            ("AUTORIZADO", "Autorizado"),  # PASO 3
            ("CANCELADO POR AUTORIZANTE", "Cancelado por autorizante"),  #
            ("REVISADO", "Revisado"),  # PASO 4
            ("CANCELADO POR REVISANTE", "Cancelado por revisante"),  #
        ]
    )

    # Nombre de la tabla
    __tablename__ = "req_requisiciones"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="req_requisiciones")
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="req_requisiciones")

    # Columnas
    fecha = db.Column(db.Date, nullable=False)
    consecutivo = db.Column(db.String(30), nullable=False)
    observaciones = db.Column(db.Text())
    estado = db.Column(
        db.Enum(*ESTADOS, name="estados", native_enum=False),
        index=True,
        nullable=False,
        default="CREADO",
        server_default="CREADO",
    )
    glosa = db.Column(db.String(30))
    programa = db.Column(db.String(60))
    fuente = db.Column(db.String(50))
    area = db.Column(db.String(100))
    fecha_requerida = db.Column(db.Date)

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

    # Columnas estado CANCELADO POR AUTORIZANTE
    reviso_cancelo_tiempo = db.Column(db.DateTime)
    reviso_cancelo_motivo = db.Column(db.String(256))
    reviso_cancelo_error = db.Column(db.String(512))

    # Hijos
    req_resguardos = db.relationship("ReqResguardo", back_populates="req_requisicion")
    req_requisiciones_registros = db.relationship("ReqRequisicionRegistro", back_populates="req_requisicion")

    def __repr__(self):
        """Representación"""
        return f"<ReqRequision {self.id}>"

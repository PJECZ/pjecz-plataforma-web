"""
Estadisticas Informes, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class EstInforme(db.Model, UniversalMixin):
    """EstInforme"""

    ESTADOS = OrderedDict(
        [
            ("BORRADOR", "Borrador"),  # PASO 1
            ("ENTREGADO", "Entregado"),  # PASO 2
            ("CANCELADO POR ENTREGANTE", "Cancelado por entregante"),  # CANCELO ENTREGANTE
            ("RECIBIDO", "Entregado"),  # PASO 3
            ("CANCELADO POR RECIBIDOR", "Cancelado por recibidor"),  # CANCELO RECIBIDOR
            ("ARCHIVADO", "Archivado"),  # PASO 4
        ]
    )

    # Nombre de la tabla
    __tablename__ = "est_informes"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autoridades_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridades = db.relationship("Autoridad", back_populates="est_informes")

    # Columnas (paso 1) estado BORRADOR
    fecha = db.Column(db.Date, index=True, nullable=False)
    estado = db.Column(
        db.Enum(*ESTADOS, name="estados", native_enum=False),
        index=True,
        nullable=False,
        default="CREADO",
        server_default="CREADO",
    )

    # Columnas (paso 2) estado ENTREGADO
    entrego_nombre = db.Column(db.String(256))
    entrego_puesto = db.Column(db.String(256))
    entrego_email = db.Column(db.String(256))
    entrego_efirma_tiempo = db.Column(db.DateTime)
    entrego_efirma_folio = db.Column(db.Integer)
    entrego_efirma_sello_digital = db.Column(db.String(512))
    entrego_efirma_url = db.Column(db.String(256))
    entrego_efirma_qr_url = db.Column(db.String(256))
    entrego_efirma_mensaje = db.Column(db.String(512))
    entrego_efirma_error = db.Column(db.String(512))

    # Columnas (cancelo entregante) estado CANCELADO POR ENTREGANTE
    entrego_cancelo_tiempo = db.Column(db.DateTime)
    entrego_cancelo_motivo = db.Column(db.String(256))
    entrego_cancelo_error = db.Column(db.String(512))

    # Columnas (paso 3) estado RECIBIDO
    recibido_nombre = db.Column(db.String(256))
    recibido_puesto = db.Column(db.String(256))
    recibido_email = db.Column(db.String(256))
    recibido_efirma_tiempo = db.Column(db.DateTime)
    recibido_efirma_folio = db.Column(db.Integer)
    recibido_efirma_sello_digital = db.Column(db.String(512))
    recibido_efirma_url = db.Column(db.String(256))
    recibido_efirma_qr_url = db.Column(db.String(256))
    recibido_efirma_mensaje = db.Column(db.String(512))
    recibido_efirma_error = db.Column(db.String(512))

    # Columnas (cancelo recibidor) estado CANCELADO POR RECIBIDOR
    recibido_cancelo_tiempo = db.Column(db.DateTime)
    recibido_cancelo_motivo = db.Column(db.String(256))
    recibido_cancelo_error = db.Column(db.String(512))

    # Hijos
    est_informes_registros = db.relationship("EstInformeRegistro", back_populates="est_informe")

    def __repr__(self):
        """Representación"""
        return f"<EstInforme {self.id}>"

"""
Financieros Vales, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class FinVale(db.Model, UniversalMixin):
    """FinVale"""

    ESTADOS = OrderedDict(
        [
            ("CREADO", "Creado"),  # PASO 1 Un usuario lo ha creado, no debe permir crear un nuevo vale si tiene uno anterior por revisar
            ("SOLICITADO", "Solicitado"),  # PASO 2 El superior lo autorizo con su firma
            ("CANCELADO POR SOLICITANTE", "Cancelado por solicitante"),  # El superior ha cancelado la firma
            ("AUTORIZADO", "Autorizado"),  # PASO 3 Finanzas lo autorizo
            ("CANCELADO POR AUTORIZANTE", "Cancelado por autorizante"),  # Finanzas ha cancelado la firma
            ("ENTREGADO", "Entregado"),  # PASO 4 El usuario lo recogió
            ("POR REVISAR", "Por revisar"),  # PASO 5 El usuario a subido los archivos adjuntos
            ("ARCHIVADO", "Archivado"),  # PASO 6 Finanzas lo archiva si cumple con la evidencia
        ]
    )

    TIPOS = OrderedDict(
        [
            ("NO DEFINIDO", "No definido"),
            ("GASOLINA", "Gasolina"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "fin_vales"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="fin_vales")

    # Columnas (step 1 create) estado CREADO
    estado = db.Column(
        db.Enum(*ESTADOS, name="estados", native_enum=False),
        index=True,
        nullable=False,
        default="CREADO",
        server_default="CREADO",
    )
    tipo = db.Column(
        db.Enum(*TIPOS, name="tipos", native_enum=False),
        index=True,
        nullable=False,
        default="GASOLINA",
        server_default="GASOLINA",
    )
    justificacion = db.Column(db.Text(), nullable=False)
    monto = db.Column(db.Float, nullable=False)

    # Columnas (step 2 request) estado SOLICITADO
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

    # Columnas (cancel 2 request) estado CANCELADO POR SOLICITANTE
    solicito_cancelo_tiempo = db.Column(db.DateTime)
    solicito_cancelo_motivo = db.Column(db.String(256))
    solicito_cancelo_error = db.Column(db.String(512))

    # Columnas (step 3 authorize) estado AUTORIZADO
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

    # Columnas (cancel 3 authorize) estado CANCELADO POR AUTORIZANTE
    autorizo_cancelo_tiempo = db.Column(db.DateTime)
    autorizo_cancelo_motivo = db.Column(db.String(256))
    autorizo_cancelo_error = db.Column(db.String(512))

    # Columnas (step 4 deliver) estado ENTREGADO
    folio = db.Column(db.String(64))

    # Columnas (step 5 attachments) estado POR REVISAR
    vehiculo_descripcion = db.Column(db.String(256))
    tanque_inicial = db.Column(db.String(48))
    tanque_final = db.Column(db.String(48))
    kilometraje_inicial = db.Column(db.Integer)
    kilometraje_final = db.Column(db.Integer)

    # Columnas (step 6 archive) estado ARCHIVADO
    notas = db.Column(db.String(1024))

    # Hijos
    fin_vales_adjuntos = db.relationship("FinValeAdjunto", back_populates="fin_vale")

    def __repr__(self):
        """Representación"""
        return f"<FinVale {self.id}>"

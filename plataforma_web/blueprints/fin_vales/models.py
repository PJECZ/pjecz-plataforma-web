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
            ("PENDIENTE", "Pendiente"),  # PASO 1 Un usuario lo ha creado, no debe permir crear un nuevo vale si tiene uno anterior por revisar
            ("ELIMINADO POR USUARIO", "Eliminado por usuario"),  # El usuario se arrepintio y lo elimino
            ("SOLICITADO", "Solicitado"),  # PASO 2 El superior lo autorizo con su firma
            ("ELIMINADO POR SOLICITANTE", "Eliminado por solicitante"),  # El superior lo elimino
            ("CANCELADO POR SOLICITANTE", "Cancelado por solicitante"),  # El superior ha canecelado la firma
            ("AUTORIZADO", "Autorizado"),  # PASO 3 Finanzas lo autorizo
            ("ELIMINADO POR AUTORIZANTE", "Eliminado por autorizante"),  # Finanzas lo elimino
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

    # Columnas PASO 1 PENDIENTE
    estado = db.Column(
        db.Enum(*ESTADOS, name="estados", native_enum=False),
        index=True,
        nullable=False,
        default="PENDIENTE",
        server_default="PENDIENTE",
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

    # Columnas PASO 2 SOLICITADO
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

    # Columnas PASO 2b CANCELADO POR SOLICITANTE
    solicito_cancelo_tiempo = db.Column(db.DateTime)
    solicito_cancelo_motivo = db.Column(db.String(256))
    solicito_cancelo_error = db.Column(db.String(512))

    # Columnas PASO 3 AUTORIZADO
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

    # Columnas PASO 3b CANCELADO POR AUTORIZANTE
    autorizo_cancelo_tiempo = db.Column(db.DateTime)
    autorizo_cancelo_motivo = db.Column(db.String(256))
    autorizo_cancelo_error = db.Column(db.String(512))

    # Columnas PASO 4 ENTREGADO
    folio = db.Column(db.String(64))

    # Columnas PASO 5 POR REVISAR
    vehiculo_descripcion = db.Column(db.String(256))
    tanque_inicial = db.Column(db.String(48))
    tanque_final = db.Column(db.String(48))
    kilometraje_inicial = db.Column(db.Integer)
    kilometraje_final = db.Column(db.Integer)

    # Columnas PASO 6 ARCHIVADO
    notas = db.Column(db.String(1024))

    # Hijos
    fin_vales_adjuntos = db.relationship("FinValeAdjunto", back_populates="fin_vale")

    def __repr__(self):
        """Representación"""
        return f"<FinVale {self.id}>"

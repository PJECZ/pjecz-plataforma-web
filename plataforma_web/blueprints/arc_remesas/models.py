"""
Archivo - Remesas, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class ArcRemesa(db.Model, UniversalMixin):
    """Archivo - Remesa"""

    ESTADOS = OrderedDict(  # varchar(16)
        [
            ("PENDIENTE", "Pendiente"),  # El SOLICITANTE comienza una solicitud de Remesa
            ("CANCELADO", "Cancelado"),  # El SOLICITANTE se arrepiente de crear una Remesa
            ("ENVIADO", "Enviado"),  # El SOLICITANTE pide que recojan la remesa. El JEFE_REMESA ve el pedido
            ("RECHAZADO", "Rechazado"),  # El JEFE_REMESA rechaza la remesa
            ("ASIGNADO", "Asignado"),  # El JEFE_REMESA acepta la remesa y la asigna a un ARCHIVISTA
            ("VERIFICADO", "Verificado"),  # El ARCHIVISTA revisa la remesa y la acepta
            ("ARCHIVADO", "Archivado"),  # El ARCHIVISTA termina de procesar la solicitud
        ]
    )

    # Nombre de la tabla
    __tablename__ = "arc_remesas"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="arc_remesas")
    usuario_asignado_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True)
    usuario_asignado = db.relationship("Usuario", back_populates="arc_remesas")

    # Columnas
    anio = db.Column(db.Integer, nullable=False)
    esta_archivado = db.Column(db.Boolean, nullable=False, default=False)
    num_oficio = db.Column(db.String(16))
    rechazo = db.Column(db.String(256))
    observaciones = db.Column(db.String(256))
    tiempo_enviado = db.Column(db.DateTime)
    estado = db.Column(
        db.Enum(*ESTADOS, name="estados", native_enum=False),
        nullable=False,
    )

    # Hijos
    arc_remesas_documentos = db.relationship("ArcRemesaDocumento", back_populates="arc_remesa", lazy="noload")
    arc_remesas_bitacoras = db.relationship("ArcRemesaBitacora", back_populates="arc_remesa", lazy="noload")

    def __repr__(self):
        """Representación"""
        return f"<Remesa> {self.id}"

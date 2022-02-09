"""
CITAS Citas, modelos
"""
from collections import OrderedDict

from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class CITCita(db.Model, UniversalMixin):
    """CITCita"""

    ESTADOS = OrderedDict(
        [
            ("ASISTIO", "Asistió"),
            ("CANCELO", "Canceló"),
            ("CONFIRMO", "Confirmó"),
            ("PENDIENTE", "Pendiente"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "cit_citas"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    servicio_id = db.Column(db.Integer, db.ForeignKey("cit_servicios.id"), index=True, nullable=False)
    servicio = db.relationship("CITServicio", back_populates="servicios")
    cliente_id = db.Column(db.Integer, db.ForeignKey("cit_clientes.id"), index=True, nullable=False)
    cliente = db.relationship("CITCliente", back_populates="clientes")
    oficina_id = db.Column(db.Integer, db.ForeignKey("oficinas.id"), index=True, nullable=False)
    oficina = db.relationship("Oficina", back_populates="oficinas")

    # Columnas
    inicio_tiempo = db.Column(db.DateTime(), nullable=False)
    termino_tiempo = db.Column(db.DateTime(), nullable=False)
    notas = db.Column(db.Text())
    estado = db.Column(db.Enum(*ESTADOS, name="tipos_estados", native_enum=False))

    # Hijos
    expedientes = db.relationship("CITExpediente", back_populates="cita")

    def __repr__(self):
        """Representación"""
        return "<Cit_Citas>"

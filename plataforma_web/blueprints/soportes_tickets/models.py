"""
Soportes Tickets, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin

# Roles necesarios
ROL_ADMINISTRADOR = "ADMINISTRADOR"
ROL_INFORMATICA = "SOPORTE INFORMATICA"
ROL_INFRAESTRUCTURA = "SOPORTE INFRAESTRUCTURA"


class SoporteTicket(db.Model, UniversalMixin):
    """SoporteTicket"""

    ESTADOS = OrderedDict(
        [
            ("SIN ATENDER", "Abierto o pendiente"),
            ("TRABAJANDO", "Trabjando"),
            ("TERMINADO", "Trabajo concluido, resultado satisfacorio"),
            ("CERRADO", "Trabajo concluido, resultado indiferente"),
            ("PENDIENTE", "Pendiente de resolver"),
            ("CANCELADO", "Cancelado"),
        ]
    )

    CLASIFICACIONES = OrderedDict(
        [
            ("SOPORTE TECNICO", "SOPORTE TÉCNICO"),
            ("PAIIJ", "PAIIJ"),
            ("SIGE", "SIGE"),
            ("INFRAESTRUCTURA", "INFRAESTRUCTURA"),
            ("OTRO", "Otro"),
        ]
    )

    DEPARTAMENTOS = OrderedDict(
        [
            ("INFORMATICA", "INFORMATICA"),
            ("INFRAESTRUCTURA", "INFRAESTRUCTURA"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "soportes_tickets"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foránea el funcionario es el técnico de soporte
    funcionario_id = db.Column(db.Integer, db.ForeignKey("funcionarios.id"), index=True, nullable=True)
    funcionario = db.relationship("Funcionario", back_populates="soportes_tickets")

    # Claves foránea la categoría
    soporte_categoria_id = db.Column(db.Integer, db.ForeignKey("soportes_categorias.id"), index=True, nullable=True)
    soporte_categoria = db.relationship("SoporteCategoria", back_populates="soportes_tickets")

    # Claves foránea el usario que solicita soporte
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="soportes_tickets")

    # Columnas
    descripcion = db.Column(db.Text, nullable=False)
    estado = db.Column(db.Enum(*ESTADOS, name="estados", native_enum=False), index=True, nullable=False)
    resolucion = db.Column(db.DateTime, nullable=True)
    soluciones = db.Column(db.Text, nullable=True)
    departamento = db.Column(db.Enum(*DEPARTAMENTOS, name="departamentos", native_enum=False), index=True, nullable=False)

    # Hijos
    soportes_adjuntos = db.relationship("SoporteAdjunto", back_populates="soporte_ticket")

    def __repr__(self):
        """Representación"""
        return "<SoporteTicket>"

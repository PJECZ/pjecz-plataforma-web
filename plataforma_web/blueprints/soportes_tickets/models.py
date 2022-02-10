"""
Soportes Tickets, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class SoporteTicket(db.Model, UniversalMixin):
    """SoporteTicket"""

    ESTADOS = OrderedDict(
        [
            ("ABIERTO", "Abierto o pendiente"),
            ("TRABAJANDO", "Trabjando"),
            ("CERRADO", "Cerrado o terminado"),
            ("NO RESUELTO", "No resuelto"),
            ("CANCELADO", "Cancelado"),
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

    # Hijos
    soportes_tickets = db.relationship('SoporteAdjunto', back_populates='soporte_ticket')

    def __repr__(self):
        """Representación"""
        return "<SoporteTicket>"

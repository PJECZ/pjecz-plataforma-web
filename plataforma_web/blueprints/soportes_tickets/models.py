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
            ("CANCELADO", "Cancelado"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "soportes_tickets"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="soportes_tickets")
    soporte_categoria_id = db.Column(db.Integer, db.ForeignKey("soportes_categorias.id"), index=True, nullable=False)
    soporte_categoria = db.relationship("SoporteCategoria", back_populates="soportes_tickets")
    funcionario_id = db.Column(db.Integer, db.ForeignKey("funcionarios.id"), index=True, nullable=False)
    funcionario = db.relationship("Funcionario", back_populates="soportes_tickets")

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    estado = db.Column(db.Enum(*ESTADOS, name="estados", native_enum=False), index=True, nullable=False)
    resolucion = db.Column(db.DateTime, nullable=True)
    soluciones = db.Column(db.Text, nullable=True)

    def __repr__(self):
        """Representación"""
        return "<SoporteTicket>"

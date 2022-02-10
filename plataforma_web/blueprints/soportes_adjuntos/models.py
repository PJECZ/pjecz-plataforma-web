"""
Soportes Adjuntos Tickets, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class SoporteAdjunto(db.Model, UniversalMixin):
    """SoporteAdjunto"""

    # Nombre de la tabla
    __tablename__ = "soportes_adjuntos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foránea para el ticket
    soporte_ticket_id = db.Column(db.Integer, db.ForeignKey("soportes_tickets.id"), index=True, nullable=True)
    soporte_ticket = db.relationship("SoporteTicket", back_populates="soportes_adjuntos")

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    archivo = db.Column(db.String(256), nullable=False, default="", server_default="")
    url = db.Column(db.String(512), nullable=False, default="", server_default="")

    def __repr__(self):
        """Representación"""
        return "<SoporteAdjunto>"

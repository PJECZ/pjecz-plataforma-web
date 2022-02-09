"""
Cit Clientes, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class CitCliente(db.Model, UniversalMixin):
    """CitCliente"""

    # Nombre de la tabla
    __tablename__ = "cit_clientes"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    nombres = db.Column(db.String(256), nullable=False)
    apellido_paterno = db.Column(db.String(256), nullable=False)
    apellido_materno = db.Column(db.String(256), default="", server_default="")
    curp = db.Column(db.String(18), unique=True, nullable=False)
    telefono = db.Column(db.String(64), default="", server_default="")
    email = db.Column(db.String(256), unique=True, nullable=False)
    contrasena = db.Column(db.String(256), nullable=False)
    hash = db.Column(db.String(32), default="", server_default="")
    renovacion_fecha = db.Column(db.Date(), nullable=False)

    # Hijos
    cit_citas = db.relationship("CitCita", back_populates="cit_cliente")

    @property
    def nombre(self):
        """Junta nombres, apellido_paterno y apellido materno"""
        return self.nombres + " " + self.apellido_paterno + " " + self.apellido_materno

    def __repr__(self):
        """Representación"""
        return "<CitCliente>"

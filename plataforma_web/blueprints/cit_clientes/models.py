"""
CITAS Clientes, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class CITCliente(db.Model, UniversalMixin):
    """ CITClientes """

    # Nombre de la tabla
    __tablename__ = 'cit_clientes'

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea

    # Columnas
    nombres = db.Column(db.String(256), nullable=False)
    apellido_paterno = db.Column(db.String(256), nullable=False)
    apellido_materno = db.Column(db.String(256), default="", server_default="")
    curp = db.Column(db.String(18), unique=True, nullable=True)
    domicilio_id = db.Column(db.Integer())
    telefono = db.Column(db.String(64))
    email = db.Column(db.String(256), nullable=False, unique=True, index=True)
    contrasena = db.Column(db.String(256), nullable=False)
    hash = db.Column(db.String(32), nullable=False, default="", server_default="")
    renovacion_fecha = db.Column(db.Date(), nullable=False)

    # Hijos


    @property
    def nombre(self):
        """Junta nombres, apellido_paterno y apellido materno"""
        return self.nombres + " " + self.apellido_paterno + " " + self.apellido_materno

    def __repr__(self):
        """ Representación """
        return '<Cit_Clientes>'

"""
Funcionarios, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Funcionario(db.Model, UniversalMixin):
    """Funcionario"""

    # Nombre de la tabla
    __tablename__ = "funcionarios"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    nombres = db.Column(db.String(256), nullable=False)
    apellido_paterno = db.Column(db.String(256), nullable=False)
    apellido_materno = db.Column(db.String(256), default="", server_default="")
    curp = db.Column(db.String(18), unique=True, index=True)
    email = db.Column(db.String(256), unique=True, index=True)
    puesto = db.Column(db.String(256), default="", server_default="")
    # numero_empleado
    # telefono_celular
    # area
    en_funciones = db.Column(db.Boolean, nullable=False, default=True)
    en_sentencias = db.Column(db.Boolean, nullable=False, default=False)
    en_soportes = db.Column(db.Boolean, nullable=False, default=False)
    en_tesis_jurisprudencias = db.Column(db.Boolean, nullable=False, default=False)

    # Hijos
    autoridades_funcionarios = db.relationship("AutoridadFuncionario", back_populates="funcionario", lazy="noload")
    funcionarios_oficinas = db.relationship('FuncionarioOficina', back_populates='funcionario', lazy="noload")
    soportes_tickets = db.relationship("SoporteTicket", back_populates="funcionario", lazy="noload")
    tesis_jurisprudencias_funcionarios = db.relationship('TesisJurisprudenciaFuncionario', back_populates='funcionario', lazy="noload")

    @property
    def nombre(self):
        """Junta nombres, apellido_paterno y apellido materno"""
        return self.nombres + " " + self.apellido_paterno + " " + self.apellido_materno

    def __repr__(self):
        """Representación"""
        return f"<Funcionario {self.nombre}>"

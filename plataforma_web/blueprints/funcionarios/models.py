"""
Funcionarios, modelos
"""
from enum import unique
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
    email = db.Column(db.String(256), unique=True, index=True)
    curp = db.Column(db.String(18), unique=True, index=True)
    puesto = db.Column(db.String(256), default="", server_default="")
    en_funciones = db.Column(db.Boolean, nullable=False, default=True)

    # Hijos
    autoridades_funcionarios = db.relationship("AutoridadFuncionario", back_populates="funcionario")

    @property
    def nombre(self):
        """Junta nombres, apellido_paterno y apellido materno"""
        return self.nombres + " " + self.apellido_paterno + " " + self.apellido_materno

    def __repr__(self):
        """Representación"""
        return f"<Funcionario {self.nombre}>"

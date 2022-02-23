"""
Funcionarios Oficinas, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class FuncionarioOficina(db.Model, UniversalMixin):
    """FuncionarioOficina"""

    # Nombre de la tabla
    __tablename__ = "funcionarios_oficinas"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    funcionario_id = db.Column(db.Integer, db.ForeignKey("funcionarios.id"), index=True, nullable=False)
    funcionario = db.relationship("Funcionario", back_populates="funcionarios_oficinas")
    oficina_id = db.Column(db.Integer, db.ForeignKey("oficinas.id"), index=True, nullable=False)
    oficina = db.relationship("Oficina", back_populates="funcionarios_oficinas")

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        """Representación"""
        return f"<FuncionarioOficina {self.descripcion}>"

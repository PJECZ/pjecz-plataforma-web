"""
Autoridades Funcionarios, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class AutoridadFuncionario(db.Model, UniversalMixin):
    """AutoridadFuncionario"""

    # Nombre de la tabla
    __tablename__ = "autoridades_funcionarios"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    autoridad_id = db.Column(db.Integer, db.ForeignKey("autoridades.id"), index=True, nullable=False)
    autoridad = db.relationship("Autoridad", back_populates="autoridades_funcionarios")
    funcionario_id = db.Column(db.Integer, db.ForeignKey('funcionarios.id'), index=True, nullable=False)
    funcionario = db.relationship('Funcionario', back_populates='autoridades_funcionarios')

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        """Representación"""
        return f"<AutoridadFuncionario {self.descripcion}>"

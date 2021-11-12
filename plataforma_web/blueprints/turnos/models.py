"""
Turnos, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Turno(db.Model, UniversalMixin):
    """Turno"""

    TIPOS = OrderedDict(
        [
            ("NORMAL", "Normal"),
            ("URGENTE", "Urgente"),
        ]
    )

    ESTADOS = OrderedDict(
        [
            ("EN ESPERA", "En Espera"),
            ("ATENDIENDO", "Atendiendo"),
            ("ATENDIDO", "Atendido"),
            ("CANCELADO", "Cancelado"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "turnos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    ventanilla_id = db.Column(db.Integer, db.ForeignKey("ventanillas.id"), index=True, nullable=False)
    ventanilla = db.relationship("Ventanilla", back_populates="turnos")
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="turnos")

    # Columnas
    numero = db.Column(db.Integer(), nullable=False)
    atencion = db.Column(db.DateTime(), nullable=False)
    termino = db.Column(db.DateTime(), nullable=False)
    comentarios = db.Column(db.String(256), nullable=False)
    tipo = db.Column(
        db.Enum(*TIPOS, name="turnos_tipos", native_enum=False),
        index=True,
        nullable=False,
    )
    estado = db.Column(
        db.Enum(*ESTADOS, name="turnos_estados", native_enum=False),
        index=True,
        nullable=False,
    )

    def __repr__(self):
        """Representación"""
        return f"<Turno {self.descripcion}>"

"""
Soportes Categorias, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class SoporteCategoria(db.Model, UniversalMixin):
    """SoporteCategoria"""

    DEPARTAMENTOS = OrderedDict(
        [
            ("TODOS", "TODOS"),
            ("INFORMATICA", "INFORMATICA"),
            ("INFRAESTRUCTURA", "INFRAESTRUCTURA"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "soportes_categorias"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    rol_id = db.Column(db.Integer, db.ForeignKey("roles.id"), index=True, nullable=False)
    rol = db.relationship("Rol", back_populates="soportes_categorias_roles")

    # Columnas
    nombre = db.Column(db.String(256), unique=True, nullable=False)
    instrucciones = db.Column(db.Text(), default="", server_default="")
    departamento = db.Column(db.Enum(*DEPARTAMENTOS, name="departamentos", native_enum=False), index=True, nullable=False)

    # Hijos
    soportes_tickets = db.relationship("SoporteTicket", back_populates="soporte_categoria")

    def __repr__(self):
        """Representación"""
        return f"<SoporteCategoria {self.nombre}>"

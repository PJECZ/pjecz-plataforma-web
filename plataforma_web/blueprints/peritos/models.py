"""
Peritos, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Perito(db.Model, UniversalMixin):
    """Perito"""

    # Nombre de la tabla
    __tablename__ = "peritos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    distrito_id = db.Column(db.Integer, db.ForeignKey("distritos.id"), index=True, nullable=False)
    distrito = db.relationship("Distrito", back_populates="peritos")

    # Clave foránea
    perito_tipo_id = db.Column(db.Integer, db.ForeignKey("peritos_tipos.id"), index=True, nullable=False)
    perito_tipo = db.relationship("PeritoTipo", back_populates="peritos")

    # Columnas
    nombre = db.Column(db.String(256), nullable=False)
    domicilio = db.Column(db.String(256), nullable=False)
    telefono_fijo = db.Column(db.String(64), default="", server_default="")
    telefono_celular = db.Column(db.String(64), default="", server_default="")
    email = db.Column(db.String(256), default="", server_default="")
    renovacion = db.Column(db.Date, nullable=False, index=True)
    notas = db.Column(db.String(256), default="", server_default="")

    def __repr__(self):
        """Representación"""
        return f"<Perito {self.nombre}>"

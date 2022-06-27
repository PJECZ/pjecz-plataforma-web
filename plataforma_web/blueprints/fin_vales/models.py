"""
Financieros Vales, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class FinVale(db.Model, UniversalMixin):
    """FinVale"""

    TIPOS = OrderedDict(
        [
            ("NO DEFINIDO", "No definido"),
            ("GASOLINA", "Gasolina"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "fin_vales"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="fin_vales")

    # Columnas
    autorizo_nombre = db.Column(db.String(256), nullable=False)
    autorizo_puesto = db.Column(db.String(256), nullable=False)
    # autorizo_email = db.Column(db.String(256), nullable=False)
    tipo = db.Column(
        db.Enum(*TIPOS, name="tipos", native_enum=False),
        index=True,
        nullable=False,
        default="NO DEFINIDO",
        server_default="NO DEFINIDO",
    )
    justificacion = db.Column(db.Text(), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    solicito_nombre = db.Column(db.String(256), nullable=False)
    solicito_puesto = db.Column(db.String(256), nullable=False)
    # solicito_email = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        """Representación"""
        return f"<FinVale {self.id}>"

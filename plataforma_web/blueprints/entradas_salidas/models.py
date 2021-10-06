"""
Entradas-Salidas, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class EntradaSalida(db.Model, UniversalMixin):
    """Bitacora"""

    TIPOS = OrderedDict(
        [
            ("INGRESO", "Ingresó"),
            ("SALIO", "Salió"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "entradas_salidas"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="entradas_salidas")

    # Columnas
    tipo = db.Column(
        db.Enum(*TIPOS, name="tipos_entradas_salidas", native_enum=False),
        index=True,
        nullable=False,
    )
    direccion_ip = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        """Representación"""
        return f"<Sesion {self.creado}: {self.tipo}>"

"""
Inventarios Componentes, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class InvComponente(db.Model, UniversalMixin):
    """InvComponente"""

    # Nombre de la tabla
    __tablename__ = "inv_componentes"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    inv_categoria_id = db.Column(db.Integer, db.ForeignKey("inv_categorias.id"), index=True, nullable=False)
    inv_categoria = db.relationship("InvCategoria", back_populates="inv_componentes")
    inv_equipo_id = db.Column(db.Integer, db.ForeignKey("inv_equipos.id"), index=True, nullable=False)
    inv_equipo = db.relationship("InvEquipo", back_populates="inv_componentes")

    # Columnas
    descripcion = db.Column(db.String(256), nullable=False)
    cantidad = db.Column(db.Integer(), nullable=False)
    version = db.Column(db.String(256))

    def __repr__(self):
        """Representación"""
        return f"<InvComponente {self.id}>"

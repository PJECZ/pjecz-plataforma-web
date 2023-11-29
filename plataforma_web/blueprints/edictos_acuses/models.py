"""
Edictos Acuses, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class EdictoAcuse(db.Model, UniversalMixin):
    """EdictoAcuse"""

    # Nombre de la tabla
    __tablename__ = "edictos_acuses"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    edicto_id = db.Column(db.Integer, db.ForeignKey("edictos.id"), index=True, nullable=False)
    edicto = db.relationship("Edicto", back_populates="edictos_acuses")

    # Columnas
    fecha = db.Column(db.Date, index=True, nullable=False)

    def __repr__(self):
        """Representación"""
        return f"<EdictoAcuse {self.id}>"

"""
Listas de Acuerdos Datos, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class ListaDeAcuerdoAcuerdo(db.Model, UniversalMixin):
    """ListaDeAcuerdoAcuerdo"""

    # Nombre de la tabla
    __tablename__ = "listas_de_acuerdos_acuerdos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    lista_de_acuerdo_id = db.Column(db.Integer, db.ForeignKey("listas_de_acuerdos.id"), index=True, nullable=False)
    lista_de_acuerdo = db.relationship("ListaDeAcuerdo", back_populates="listas_de_acuerdos_acuerdos")

    # Columnas
    folio = db.Column(db.String(16), nullable=False)
    expediente = db.Column(db.String(16), nullable=False)
    actor = db.Column(db.String(256), nullable=False)
    demandado = db.Column(db.String(256), nullable=False)
    tipo_acuerdo = db.Column(db.String(256), nullable=False)
    tipo_juicio = db.Column(db.String(256), nullable=False)
    referencia = db.Column(db.Integer(), nullable=False)

    def __repr__(self):
        """Representación"""
        return "<ListaDeAcuerdoAcuerdo>"

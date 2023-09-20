"""
Estadisticas Informes Registros, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class EstInformeRegistro(db.Model, UniversalMixin):
    """EstInformeRegistro"""

    # Nombre de la tabla
    __tablename__ = "est_informes_registros"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    est_informe_id = db.Column(db.Integer, db.ForeignKey("est_informes.id"), index=True, nullable=False)
    est_informe = db.relationship("EstInforme", back_populates="est_informes_registros")
    est_variable_id = db.Column(db.Integer, db.ForeignKey("est_variables.id"), index=True, nullable=False)
    est_variable = db.relationship("EstVariable", back_populates="est_informes_registros")

    # Columnas
    cantidad = db.Column(db.Integer())

    def __repr__(self):
        """Representación"""
        return f"<EstInformeRegistro {self.id}>"

"""
Estadisticas Variables, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class EstVariable(db.Model, UniversalMixin):
    """EstVariable"""

    # Nombre de la tabla
    __tablename__ = "est_variables"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Columnas
    clave = db.Column(db.String(16), unique=True, nullable=False)
    descripcion = db.Column(db.String(256), nullable=False)

    # Hijos
    # est_informes_registros = db.relationship('EstInformeRegistro', back_populates='est_variable', lazy='noload')

    def __repr__(self):
        """Representación"""
        return f"<EstVariable {self.clave}>"

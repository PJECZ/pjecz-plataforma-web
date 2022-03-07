"""
REPSVM Agresores, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class REPSVMAgresor(db.Model, UniversalMixin):
    """REPSVMAgresor"""

    # Nombre de la tabla
    __tablename__ = "repsvm_agresores"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    distrito_id = db.Column(db.Integer, db.ForeignKey("distritos.id"), index=True, nullable=False)
    distrito = db.relationship("Distrito", back_populates="repsvm_agresores")
    materia_tipo_juzgado_id = db.Column(db.Integer, db.ForeignKey("materias_tipos_juzgados.id"), index=True, nullable=False)
    materia_tipo_juzgado = db.relationship("MateriaTipoJuzgado", back_populates="repsvm_agresores")
    repsvm_delito_especifico_id = db.Column(db.Integer, db.ForeignKey("repsvm_delitos_especificos.id"), index=True, nullable=False)
    repsvm_delito_especifico = db.relationship("REPSVMDelitoEspecifico", back_populates="repsvm_agresores")
    repsvm_tipo_sentencia_id = db.Column(db.Integer, db.ForeignKey("repsvm_tipos_sentencias.id"), index=True, nullable=False)
    repsvm_tipo_sentencia = db.relationship("REPSVMTipoSentencia", back_populates="repsvm_agresores")

    # Columnas
    pena_impuesta = db.Column(db.String(256), nullable=False)
    observaciones = db.Column(db.Text, nullable=True)
    sentencia_archivo = db.Column(db.String(256), nullable=False)
    sentencia_url = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        """Representación"""
        return f"<REPSVMAgresor {self.id}>"

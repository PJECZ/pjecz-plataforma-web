"""
Oficinas, modelos
"""
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class Oficina(db.Model, UniversalMixin):
    """Oficina"""

    # Nombre de la tabla
    __tablename__ = "oficinas"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    distrito_id = db.Column(db.Integer, db.ForeignKey("distritos.id"), index=True, nullable=False)
    distrito = db.relationship("Distrito", back_populates="oficinas")
    domicilio_id = db.Column(db.Integer, db.ForeignKey("domicilios.id"), index=True, nullable=False)
    domicilio = db.relationship("Domicilio", back_populates="oficinas")

    # Columnas
    clave = db.Column(db.String(32), unique=True, nullable=False)
    descripcion = db.Column(db.String(512), nullable=False)
    descripcion_corta = db.Column(db.String(64), nullable=False)
    es_jurisdiccional = db.Column(db.Boolean, nullable=False, default=False)
    apertura = db.Column(db.Time(), nullable=False)
    cierre = db.Column(db.Time(), nullable=False)
    limite_personas = db.Column(db.Integer(), nullable=False)

    # Hijos
    cit_citas = db.relationship("CitCita", back_populates="oficina", lazy="noload")
    funcionarios_oficinas = db.relationship('FuncionarioOficina', back_populates='oficina', lazy="noload")
    usuarios = db.relationship("Usuario", back_populates="oficina", lazy="noload")

    @property
    def clave_nombre(self):
        """Entrega clave - descripcion corta para usar en select"""
        return f"{self.clave} — {self.descripcion_corta}"

    def __repr__(self):
        """Representación"""
        return f"<Oficina> {self.clave}"

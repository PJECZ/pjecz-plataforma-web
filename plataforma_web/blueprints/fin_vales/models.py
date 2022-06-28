"""
Financieros Vales, modelos
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class FinVale(db.Model, UniversalMixin):
    """FinVale"""

    ESTADOS = OrderedDict(
        [
            ("PENDIENTE", "Pendiente"),
            ("SOLICITADO", "Solicitado"),
            ("AUTORIZADO", "Autorizado"),
            ("COMPROBADO", "Comprobado"),
            ("CANCELADO", "Cancelado"),
        ]
    )

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

    # Columnas que deben pre-llenarse
    solicito_nombre = db.Column(db.String(256), nullable=False)
    solicito_puesto = db.Column(db.String(256), nullable=False)
    solicito_email = db.Column(db.String(256), nullable=False)
    autorizo_nombre = db.Column(db.String(256), nullable=False)
    autorizo_puesto = db.Column(db.String(256), nullable=False)
    autorizo_email = db.Column(db.String(256), nullable=False)

    # Columnas que en el estado PENDIENTE se pueden modificar
    estados = db.Column(
        db.Enum(*ESTADOS, name="estados", native_enum=False),
        index=True,
        nullable=False,
        default="NO DEFINIDO",
        server_default="NO DEFINIDO",
    )
    tipo = db.Column(
        db.Enum(*TIPOS, name="tipos", native_enum=False),
        index=True,
        nullable=False,
        default="NO DEFINIDO",
        server_default="NO DEFINIDO",
    )
    justificacion = db.Column(db.Text(), nullable=False)
    monto = db.Column(db.Float, nullable=False)

    # Columnas que en el estado SOLICITADO reciben valores
    solicito_efirma_tiempo = db.Column(db.DateTime)
    solicito_efirma_folio = db.Column(db.Integer)
    solicito_efirma_selloDigital = db.Column(db.String(512))
    solicito_efirma_url = db.Column(db.String(256))
    solicito_efirma_qr_url = db.Column(db.String(256))

    # Columnas que en el estado AUTORIZADO reciben valores
    autorizo_efirma_tiempo = db.Column(db.DateTime)
    autorizo_efirma_folio = db.Column(db.Integer)
    autorizo_efirma_selloDigital = db.Column(db.String(512))
    autorizo_efirma_url = db.Column(db.String(256))
    autorizo_efirma_qr_url = db.Column(db.String(256))

    # Columnas que en el estado COMPROBADO reciben valores
    vehiculo_descripcion = db.Column(db.String(256))
    tanque_inicial = db.Column(db.String(256))
    tanque_final = db.Column(db.String(256))
    kilometraje_inicial = db.Column(db.Integer)
    kilometraje_final = db.Column(db.Integer)

    # Hijos
    # fin_vales_adjuntos

    def __repr__(self):
        """Representación"""
        return f"<FinVale {self.id}>"

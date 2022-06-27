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

    # Columnas
    autorizo_nombre = db.Column(db.String(256), nullable=False)
    autorizo_puesto = db.Column(db.String(256), nullable=False)
    # autorizo_email = db.Column(db.String(256), nullable=False)
    # autorizo_efirma_folio
    # autorizo_efirma_selloDigital
    # autorizo_efirma_url
    # autorizo_efirma_url
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
    solicito_nombre = db.Column(db.String(256), nullable=False)
    solicito_puesto = db.Column(db.String(256), nullable=False)
    # solicito_email = db.Column(db.String(256), nullable=False)
    # solicito_efirma_folio
    # solicito_efirma_selloDigital
    # solicito_efirma_url
    # solicito_efirma_qr_url

    # vehiculo_descripcion
    # tanque_inicial
    # tanque_final
    # kilometraje_inicial
    # kilometraje_final

    # Hijos
    # fin_vales_adjuntos

    def __repr__(self):
        """Representación"""
        return f"<FinVale {self.id}>"

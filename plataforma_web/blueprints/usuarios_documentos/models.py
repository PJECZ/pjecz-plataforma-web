"""
Usuarios Documentos, modelos

Datos personales de los usuarios
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class UsuarioDocumento(db.Model, UniversalMixin):
    """UsuarioDocumento"""

    ESTADOS_CIVILES = OrderedDict(
        [
            ("CASADO", "Casado"),
            ("DIVORCIADO", "Divorciado"),
            ("SOLTERO", "Soltero"),
            ("UNION LIBRE", "Unión Libre"),
            ("VIUDO", "Viudo"),
        ]
    )

    VALIDACIONES = OrderedDict(
        [
            ("POR VALIDAR", "Pendiente por validar"),
            ("NO VALIDO", "Con errores"),
            ("VALIDO", "Válido"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "usuarios_documentos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="usuarios_documentos")

    # Columnas
    curp = db.Column(db.String(18), unique=True, nullable=False)
    # Campos del formulario
    url_identificacion = db.Column(db.String(512))
    url_cp_fiscal = db.Column(db.String(512))
    url_domicilio = db.Column(db.String(512))
    url_acta_nacimiento = db.Column(db.String(512))
    url_estudios = db.Column(db.String(512))
    cp_fiscal = db.Column(db.Integer)
    domicilio_calle = db.Column(db.String(255))
    domicilio_colonia = db.Column(db.String(64))
    domicilio_numero = db.Column(db.String(16))
    domicilio_ciudad = db.Column(db.String(32))
    domicilio_estado = db.Column(db.String(32))
    es_madre = db.Column(db.Boolean)
    estado_civil = db.Column(
        db.Enum(*ESTADOS_CIVILES, name="estado_civil", native_enum=False),
    )
    telefono_personal = db.Column(db.String(16))
    email_personal = db.Column(db.String(64))
    # Estados de los campos
    estado_identificacion = db.Column(db.Enum(*VALIDACIONES, name="estado_identificacion", native_enum=False))
    estado_cp_fiscal = db.Column(db.Enum(*VALIDACIONES, name="estado_cp_fiscal", native_enum=False))
    estado_domicilio = db.Column(db.Enum(*VALIDACIONES, name="estado_domicilio", native_enum=False))
    estado_acta_nacimiento = db.Column(db.Enum(*VALIDACIONES, name="estado_acta_nacimiento", native_enum=False))
    estado_estudios = db.Column(db.Enum(*VALIDACIONES, name="estado_estudios", native_enum=False))
    estado_estado_civil = db.Column(db.Enum(*VALIDACIONES, name="estado_estado_civil", native_enum=False))
    estado_telefono = db.Column(db.Enum(*VALIDACIONES, name="estado_telefono", native_enum=False))
    estado_email = db.Column(db.Enum(*VALIDACIONES, name="estado_email", native_enum=False))
    estado_general = db.Column(db.Enum(*VALIDACIONES, name="estado_general", native_enum=False))
    # Mensajes de los campos en caso de no ser válidos
    mensaje_identificacion = db.Column(db.String(255))
    mensaje_cp_fiscal = db.Column(db.String(255))
    mensaje_domicilio = db.Column(db.String(255))
    mensaje_acta_nacimiento = db.Column(db.String(255))
    mensaje_estudios = db.Column(db.String(255))
    mensaje_estado_civil = db.Column(db.String(255))
    mensaje_telefono = db.Column(db.String(255))
    mensaje_email = db.Column(db.String(255))

    def __repr__(self):
        """Representación"""
        return "<UsuarioDocumento> {id}"
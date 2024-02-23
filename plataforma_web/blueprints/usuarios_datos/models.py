"""
Usuarios Datos, modelos

Datos personales de los usuarios
"""
from collections import OrderedDict
from plataforma_web.extensions import db
from lib.universal_mixin import UniversalMixin


class UsuarioDato(db.Model, UniversalMixin):
    """UsuarioDato"""

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
            ("INCOMPLETO", "Incompleto"),
        ]
    )

    # Nombre de la tabla
    __tablename__ = "usuarios_datos"

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Clave foránea
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), index=True, nullable=False)
    usuario = db.relationship("Usuario", back_populates="usuarios_datos")

    # Columnas
    # Campos para archivos adjuntos
    adjunto_identificacion_id = db.Column(db.Integer)
    adjunto_acta_nacimiento_id = db.Column(db.Integer)
    adjunto_domicilio_id = db.Column(db.Integer)
    adjunto_curp_id = db.Column(db.Integer)
    adjunto_cp_fiscal_id = db.Column(db.Integer)
    adjunto_curriculum_id = db.Column(db.Integer)
    adjunto_estudios_id = db.Column(db.Integer)
    adjunto_acta_nacimiento_hijo_id = db.Column(db.Integer)
    adjunto_estado_cuenta_id = db.Column(db.Integer)
    # Campos como textos
    curp = db.Column(db.String(18))
    fecha_nacimiento = db.Column(db.Date)
    cp_fiscal = db.Column(db.Integer)
    domicilio_calle = db.Column(db.String(255))
    domicilio_numero_ext = db.Column(db.String(8))
    domicilio_numero_int = db.Column(db.String(8))
    domicilio_colonia = db.Column(db.String(64))
    domicilio_ciudad = db.Column(db.String(32))
    domicilio_estado = db.Column(db.String(32))
    domicilio_cp = db.Column(db.Integer)
    es_madre = db.Column(db.Boolean)
    estado_civil = db.Column(
        db.Enum(*ESTADOS_CIVILES, name="estado_civil", native_enum=False),
    )
    estudios_cedula = db.Column(db.String(16))
    telefono_personal = db.Column(db.String(16))
    email_personal = db.Column(db.String(64))
    # Estados de los campos
    estado_identificacion = db.Column(db.Enum(*VALIDACIONES, name="estado_identificacion", native_enum=False), default="INCOMPLETO")
    estado_acta_nacimiento = db.Column(db.Enum(*VALIDACIONES, name="estado_identificacion", native_enum=False), default="INCOMPLETO")
    estado_domicilio = db.Column(db.Enum(*VALIDACIONES, name="estado_domicilio", native_enum=False), default="INCOMPLETO")
    estado_curp = db.Column(db.Enum(*VALIDACIONES, name="estado_domicilio", native_enum=False), default="INCOMPLETO")
    estado_cp_fiscal = db.Column(db.Enum(*VALIDACIONES, name="estado_cp_fiscal", native_enum=False), default="INCOMPLETO")
    estado_curriculum = db.Column(db.Enum(*VALIDACIONES, name="estado_cp_fiscal", native_enum=False), default="INCOMPLETO")
    estado_estudios = db.Column(db.Enum(*VALIDACIONES, name="estado_estudios", native_enum=False), default="INCOMPLETO")
    estado_es_madre = db.Column(db.Enum(*VALIDACIONES, name="estado_acta_nacimiento", native_enum=False), default="INCOMPLETO")
    estado_estado_civil = db.Column(db.Enum(*VALIDACIONES, name="estado_estado_civil", native_enum=False), default="INCOMPLETO")
    estado_estado_cuenta = db.Column(db.Enum(*VALIDACIONES, name="estado_estado_civil", native_enum=False), default="INCOMPLETO")
    estado_telefono = db.Column(db.Enum(*VALIDACIONES, name="estado_telefono", native_enum=False), default="INCOMPLETO")
    estado_email = db.Column(db.Enum(*VALIDACIONES, name="estado_email", native_enum=False), default="INCOMPLETO")
    estado_general = db.Column(db.Enum(*VALIDACIONES, name="estado_general", native_enum=False), default="INCOMPLETO")
    # Mensajes de los campos en caso de no ser válidos
    mensaje_identificacion = db.Column(db.String(255))
    mensaje_acta_nacimiento = db.Column(db.String(255))
    mensaje_domicilio = db.Column(db.String(255))
    mensaje_curp = db.Column(db.String(255))
    mensaje_cp_fiscal = db.Column(db.String(255))
    mensaje_curriculum = db.Column(db.String(255))
    mensaje_estudios = db.Column(db.String(255))
    mensaje_es_madre = db.Column(db.String(255))
    mensaje_estado_civil = db.Column(db.String(255))
    mensaje_estado_cuenta = db.Column(db.String(255))
    mensaje_telefono = db.Column(db.String(255))
    mensaje_email = db.Column(db.String(255))

    def __repr__(self):
        """Representación"""
        return "<UsuarioDato> {id}"

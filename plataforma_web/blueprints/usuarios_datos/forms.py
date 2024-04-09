"""
Usuarios Datos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, IntegerField, RadioField
from wtforms.validators import DataRequired, Optional, ValidationError
from flask_wtf.file import FileField, FileRequired

from plataforma_web.blueprints.usuarios_datos.models import UsuarioDato


def FileSizeLimit(max_size_in_mb):
    max_bytes = max_size_in_mb * 1024 * 1024

    def file_length_check(form, field):
        if len(field.data.read()) > max_bytes:
            raise ValidationError(f"El tamaño del archivo es demasiado grande. Máximo permitido: {max_size_in_mb} MB")
        field.data.seek(0)

    return file_length_check


class UsuarioDatoEditIdentificacionForm(FlaskForm):
    """Formulario Edit Identificación Oficial"""

    archivo = FileField("Archivo PDF o JPG", validators=[FileRequired(), FileSizeLimit(5)])
    guardar = SubmitField("Guardar")


class UsuarioDatoEditActaNacimientoForm(FlaskForm):
    """Formulario Edit Acta de Nacimiento"""

    archivo = FileField("Archivo PDF o JPG", validators=[Optional(), FileSizeLimit(5)])
    fecha_nacimiento = DateField("Fecha de Nacimiento", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class UsuarioDatoEditDomicilioForm(FlaskForm):
    """Formulario Edit Domicilio"""

    archivo = FileField("Archivo PDF o JPG", validators=[Optional(), FileSizeLimit(5)])
    calle = StringField("Calle", validators=[DataRequired()])
    numero_exterior = StringField("Número Exterior", validators=[DataRequired()])
    numero_interior = StringField("Número Interior", validators=[Optional()])
    colonia = StringField("Colonia", validators=[DataRequired()])
    ciudad = StringField("Ciudad", validators=[DataRequired()])
    estado = StringField("Estado", validators=[DataRequired()])
    codigo_postal = IntegerField("Código Postal", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class UsuarioDatoEditCurpForm(FlaskForm):
    """Formulario Edit CURP"""

    archivo = FileField("Archivo PDF o JPG", validators=[Optional(), FileSizeLimit(5)])
    curp = StringField("CURP", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class UsuarioDatoEditCPFiscalForm(FlaskForm):
    """Formulario Edit Código postal Fiscal"""

    archivo = FileField("Archivo PDF o JPG", validators=[Optional(), FileSizeLimit(5)])
    cp_fiscal = IntegerField("Código Postal Fiscal", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class UsuarioDatoEditCurriculumForm(FlaskForm):
    """Formulario Edit Curriculum"""

    archivo = FileField("Archivo PDF o JPG", validators=[FileRequired(), FileSizeLimit(10)])
    guardar = SubmitField("Guardar")


class UsuarioDatoEditEstudiosForm(FlaskForm):
    """Formulario Edit Cédula Profesional"""

    archivo = FileField("Archivo PDF o JPG", validators=[Optional(), FileSizeLimit(5)])
    cedula_profesional = StringField("Cédula Profesional", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class UsuarioDatoEditEsMadreForm(FlaskForm):
    """Formulario Edit Es Madre, Acta de Nacimiento de un hijo"""

    archivo = FileField("Archivo PDF o JPG", validators=[Optional(), FileSizeLimit(5)])
    es_madre = RadioField("Soy Madre", choices=["SI", "NO"], default="NO", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class UsuarioDatoEditEstadoCivilForm(FlaskForm):
    """Formulario Edit Estado Civil"""

    estado_civil = SelectField("Estado Civil", choices=UsuarioDato.ESTADOS_CIVILES, validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class UsuarioDatoEditEstadoCuentaForm(FlaskForm):
    """Formulario Edit Estado de Cuenta"""

    archivo = FileField("Archivo PDF o JPG", validators=[FileRequired(), FileSizeLimit(5)])
    guardar = SubmitField("Guardar")


class UsuarioDatoValidateForm(FlaskForm):
    """Formulario para validar"""

    mensaje = StringField("Mensaje", validators=[Optional()])
    valido = SubmitField("Válido")
    no_valido = SubmitField("No Válido")

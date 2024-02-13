"""
Usuarios Datos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, IntegerField, RadioField
from wtforms.validators import DataRequired, Length, Optional
from flask_wtf.file import FileField, FileRequired

from plataforma_web.blueprints.usuarios_datos.models import UsuarioDato


class UsuarioDatoEditIdentificacionForm(FlaskForm):
    """Formulario Edit Identificación Oficial"""

    archivo = FileField("Archivo PDF o JPG", validators=[FileRequired()])
    guardar = SubmitField("Guardar")


class UsuarioDatoEditActaNacimientoForm(FlaskForm):
    """Formulario Edit Acta de Nacimiento"""

    archivo = FileField("Archivo PDF o JPG", validators=[Optional()])
    fecha_nacimiento = DateField("Fecha de Nacimiento", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class UsuarioDatoEditDomicilioForm(FlaskForm):
    """Formulario Edit Domicilio"""

    archivo = FileField("Archivo PDF o JPG", validators=[Optional()])
    calle = StringField("Calle", validators=[DataRequired()])
    numero_exterior = StringField("Número Exterior", validators=[DataRequired()])
    numero_interior = StringField("Número Interior", validators=[Optional()])
    colonia = StringField("Colonia", validators=[DataRequired()])
    ciudad = StringField("Ciudad", validators=[DataRequired()])
    estado = StringField("Estado", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class UsuarioDatoEditCurpForm(FlaskForm):
    """Formulario Edit CURP"""

    archivo = FileField("Archivo PDF o JPG", validators=[Optional()])
    curp = StringField("CURP", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class UsuarioDatoEditCPFiscalForm(FlaskForm):
    """Formulario Edit Código postal Fiscal"""

    archivo = FileField("Archivo PDF o JPG", validators=[Optional()])
    cp_fiscal = IntegerField("Código Postal Fiscal", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class UsuarioDatoEditCurriculumForm(FlaskForm):
    """Formulario Edit Curriculum"""

    archivo = FileField("Archivo PDF o JPG", validators=[FileRequired()])
    guardar = SubmitField("Guardar")


class UsuarioDatoEditEstudiosForm(FlaskForm):
    """Formulario Edit Cédula Profesional"""

    archivo = FileField("Archivo PDF o JPG", validators=[Optional()])
    cedula_profesional = StringField("Cédula Profesional", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class UsuarioDatoEditEsMadreForm(FlaskForm):
    """Formulario Edit Es Madre, Acta de Nacimiento de un hijo"""

    archivo = FileField("Archivo PDF o JPG", validators=[Optional()])
    es_madre = RadioField("Soy Madre", choices=["SI", "NO"], default="NO", validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class UsuarioDatoEditEstadoCivilForm(FlaskForm):
    """Formulario Edit Estado Civil"""

    estado_civil = SelectField("Estado Civil", choices=UsuarioDato.ESTADOS_CIVILES, validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class UsuarioDatoEditEstadoCuentaForm(FlaskForm):
    """Formulario Edit Estado de Cuenta"""

    archivo = FileField("Archivo PDF o JPG", validators=[FileRequired()])
    guardar = SubmitField("Guardar")


class UsuarioDatoValidateForm(FlaskForm):
    """Formulario para validar"""

    mensaje = StringField("Mensaje", validators=[Optional()])
    valido = SubmitField("Válido")
    no_valido = SubmitField("No Válido")

"""
SIGA Salas, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from plataforma_web.blueprints.siga_salas.models import SIGASala
from lib.safe_string import DIRECCION_IP_REGEXP


class SIGASalaNewForm(FlaskForm):
    """Formulario para nueva Salas"""

    clave = StringField("Clave", validators=[DataRequired(), Length(min=4, max=16)])
    edificio = SelectField("Edificio", coerce=int, validate_choice=False, validators=[DataRequired()])
    direccion_ip = StringField("Dirección IP", validators=[Optional(), Length(max=16), Regexp(DIRECCION_IP_REGEXP)])
    direccion_nvr = StringField("Dirección NVR", validators=[Optional(), Length(max=16), Regexp(DIRECCION_IP_REGEXP)])
    descripcion = TextAreaField("Descripción", validators=[Optional(), Length(max=1024)])
    crear = SubmitField("Crear")


class SIGASalaEditForm(FlaskForm):
    """Formulario para editar Salas"""

    clave = StringField("Clave")
    edificio = SelectField("Edificio", coerce=int, validate_choice=False, validators=[DataRequired()])
    direccion_ip = StringField("Dirección IP", validators=[Optional(), Length(max=16), Regexp(DIRECCION_IP_REGEXP)])
    direccion_nvr = StringField("Dirección NVR", validators=[Optional(), Length(max=16), Regexp(DIRECCION_IP_REGEXP)])
    descripcion = TextAreaField("Descripción", validators=[Optional(), Length(max=1024)])
    estado = SelectField("Estado", choices=SIGASala.ESTADOS, validators=[DataRequired()])
    guardar = SubmitField("Guardar")

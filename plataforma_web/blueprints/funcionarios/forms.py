"""
Funcionarios, formularios
"""
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp

from lib.safe_string import CURP_REGEXP


class FuncionarioForm(FlaskForm):
    """ Formulario Funcionario """
    nombres = StringField("Nombres", validators=[DataRequired(), Length(max=256)])
    apellido_paterno = StringField("Apellido paterno", validators=[DataRequired(), Length(max=256)])
    apellido_materno = StringField("Apellido materno", validators=[Optional(), Length(max=256)])
    curp = StringField("CURP", validators=[Optional(), Length(min=18, max=18), Regexp(CURP_REGEXP, 0, "CURP inválida")])
    puesto = StringField("Puesto", validators=[Optional(), Length(max=256)])
    email = StringField("e-mail", validators=[Optional(), Email()])
    en_funciones = BooleanField("En funciones", validators=[Optional()])
    guardar = SubmitField('Guardar')

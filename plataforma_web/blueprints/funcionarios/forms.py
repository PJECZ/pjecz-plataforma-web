"""
Funcionarios, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional


class FuncionarioForm(FlaskForm):
    """ Formulario Funcionario """
    nombres = StringField("Nombres", validators=[DataRequired(), Length(max=256)])
    apellido_paterno = StringField("Apellido paterno", validators=[DataRequired(), Length(max=256)])
    apellido_materno = StringField("Apellido materno", validators=[Optional(), Length(max=256)])
    email = StringField("e-mail", validators=[DataRequired(), Email()])
    guardar = SubmitField('Guardar')

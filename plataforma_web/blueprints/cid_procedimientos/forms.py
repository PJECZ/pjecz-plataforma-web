"""
CID Procedimientos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class ProcedimientoForm(FlaskForm):
    """ Formulario Procedimiento """

    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=256)])
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")

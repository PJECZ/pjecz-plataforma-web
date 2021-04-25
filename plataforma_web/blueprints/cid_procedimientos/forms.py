"""
CID Procedimientos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class ProcedimientoForm(FlaskForm):
    """ Formulario Procedimiento """

    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")

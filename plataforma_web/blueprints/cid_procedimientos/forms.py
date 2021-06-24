"""
CID Procedimientos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class CIDProcedimientoForm(FlaskForm):
    """ Formulario CID Procedimiento """

    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    contenido = HiddenField("Contenido", validators=[DataRequired()])
    guardar = SubmitField("Guardar")

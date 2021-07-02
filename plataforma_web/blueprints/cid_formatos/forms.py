"""
CID Formatos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class CIDFormatoForm(FlaskForm):
    """ Formulario CID Formato """

    procedimiento = StringField("Procedimiento")  # Read only
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField("Guardar")

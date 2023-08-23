"""
CID Areas, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class CIDAreaForm(FlaskForm):
    """ Formulario CIDArea """
    clave = StringField("Clave (única, máximo 16 caracteres)", validators=[DataRequired(), Length(max=16)])
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField('Guardar')

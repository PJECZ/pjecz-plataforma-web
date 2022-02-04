"""
Domicilios, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, Optional


class DomicilioForm(FlaskForm):
    """Formulario para Domicilios"""

    colonia = StringField("Colonia", validators=[DataRequired(), Length(max=256)])
    calle = StringField("Calle", validators=[DataRequired(), Length(max=256)])
    cp = IntegerField('CP', validators=[Optional()])
    num_ext = IntegerField("Núm. Exterior", validators=[Optional()])
    num_int = IntegerField("Núm. Interior", validators=[Optional()])
    guardar = SubmitField("Guardar")


class DomicilioSearchForm(FlaskForm):
    """Formulario para Buscar Domicilios"""

    colonia = StringField("Colonia", validators=[Optional(), Length(max=256)])
    calle = StringField("Calle", validators=[Optional(), Length(max=256)])
    cp = IntegerField('CP', validators=[Optional()])
    buscar = SubmitField("Buscar")

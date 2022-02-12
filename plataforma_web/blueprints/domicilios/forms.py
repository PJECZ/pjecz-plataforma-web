"""
Domicilios, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, Optional


class DomicilioForm(FlaskForm):
    """Formulario para Domicilios"""

    estado = StringField("Estado", validators=[DataRequired(), Length(max=64)])
    municipio = StringField("Municipio", validators=[DataRequired(), Length(max=64)])
    calle = StringField("Calle", validators=[DataRequired(), Length(max=256)])
    num_ext = StringField("Núm. Exterior", validators=[Optional()])
    num_int = StringField("Núm. Interior", validators=[Optional()])
    colonia = StringField("Colonia", validators=[Optional(), Length(max=256)])
    cp = IntegerField('CP', validators=[DataRequired()])
    guardar = SubmitField("Guardar")


class DomicilioSearchForm(FlaskForm):
    """Formulario para Buscar Domicilios"""

    colonia = StringField("Colonia", validators=[Optional(), Length(max=256)])
    calle = StringField("Calle", validators=[Optional(), Length(max=256)])
    cp = IntegerField('CP', validators=[Optional()])
    buscar = SubmitField("Buscar")

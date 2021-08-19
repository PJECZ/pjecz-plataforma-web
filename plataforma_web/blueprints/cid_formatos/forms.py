"""
CID Formatos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

from plataforma_web.blueprints.cid_formatos.models import CIDFormato


class CIDFormatoForm(FlaskForm):
    """Formulario CID Formato"""

    procedimiento = StringField("Procedimiento")  # Read only
    numero = IntegerField("Número", validators=[DataRequired()])
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    codigo = StringField("Código", validators=[DataRequired(), Length(max=16)])
    responsable = StringField("Responsable", validators=[DataRequired(), Length(max=128)])
    forma = SelectField("Forma", choices=CIDFormato.FORMAS, validators=[DataRequired()])
    tiempo_retencion = StringField("Tiempo de retención", validators=[DataRequired(), Length(max=48)])
    guardar = SubmitField("Guardar")

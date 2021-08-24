"""
Rep Graficas, formularios
"""
from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

from plataforma_web.blueprints.rep_graficas.models import RepGrafica


class RepGraficaForm(FlaskForm):
    """Formulario RepGrafica"""

    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    desde = DateField("Desde", validators=[DataRequired()])
    hasta = DateField("Hasta", validators=[DataRequired()])
    corte = SelectField("Corte", choices=RepGrafica.CORTES, validators=[DataRequired()])
    guardar = SubmitField("Guardar")

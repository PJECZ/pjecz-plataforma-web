"""
Reportes, formularios
"""
from flask_wtf import FlaskForm
from wtforms import DateTimeField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

from plataforma_web.blueprints.reportes.models import Reporte


class ReporteForm(FlaskForm):
    """Formulario Reporte"""

    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    desde = DateTimeField("Desde", validators=[DataRequired()])
    hasta = DateTimeField("Hasta", validators=[DataRequired()])
    programado = DateTimeField("Programado", validators=[DataRequired()])
    progreso = SelectField("Progreso", choices=Reporte.PROGRESOS, validators=[DataRequired()])
    guardar = SubmitField("Guardar")

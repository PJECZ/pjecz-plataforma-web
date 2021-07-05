"""
Rep Reportes, formularios
"""
from flask_wtf import FlaskForm
from wtforms import DateTimeField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

from plataforma_web.blueprints.rep_reportes.models import RepReporte


class RepReporteForm(FlaskForm):
    """Formulario Reporte"""

    rep_grafica = StringField("Gráfica") # Read only
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=256)])
    desde = DateTimeField("Desde", validators=[DataRequired()])
    hasta = DateTimeField("Hasta", validators=[DataRequired()])
    programado = DateTimeField("Programado", validators=[DataRequired()])
    progreso = SelectField("Progreso", choices=RepReporte.PROGRESOS, validators=[DataRequired()])
    guardar = SubmitField("Guardar")

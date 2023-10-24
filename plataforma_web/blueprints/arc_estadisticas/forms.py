"""
Arc Estadisticas, formularios
"""
from flask_wtf import FlaskForm
from wtforms import SubmitField, DateField
from wtforms.validators import DataRequired


class ArcEstadisticasForm(FlaskForm):
    """Formulario ArcEstadisticas"""

    fecha_desde = DateField("Desde", validators=[DataRequired()])
    fecha_hasta = DateField("Hasta", validators=[DataRequired()])
    elaborar = SubmitField("Elaborar")

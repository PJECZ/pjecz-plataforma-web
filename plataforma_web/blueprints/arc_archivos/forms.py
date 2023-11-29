"""
Arc Archivo, formularios
"""
from flask_wtf import FlaskForm
from wtforms import SubmitField, DateField
from wtforms.validators import DataRequired


class ArcEstadisticasDateRangeForm(FlaskForm):
    """Formulario para estadísticas por rangos de fechas"""

    fecha_desde = DateField("Desde", validators=[DataRequired()])
    fecha_hasta = DateField("Hasta", validators=[DataRequired()])
    totales = SubmitField("Totales")
    por_distritos = SubmitField("Por Distritos")
    por_instancias = SubmitField("Por Instancias")
    por_archivistas = SubmitField("Por Archivistas")

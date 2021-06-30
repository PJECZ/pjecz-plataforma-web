"""
CID Procedimientos, formularios
"""
from flask_wtf import FlaskForm
from wtforms import DateField, HiddenField, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

from plataforma_web.blueprints.cid_procedimientos.models import CIDProcedimiento


class CIDProcedimientoForm(FlaskForm):
    """Formulario CID Procedimiento"""

    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=128)])
    codigo = StringField("Código", validators=[DataRequired(), Length(max=16)])
    revision = IntegerField("Revisión", validators=[DataRequired()])
    fecha = DateField("Fecha", validators=[DataRequired()])
    etapa = SelectField("Etapa", choices=CIDProcedimiento.ETAPAS, validators=[DataRequired()])
    contenido = HiddenField("Contenido", validators=None)  # Por javascript se copia del Quill
    guardar = SubmitField("Guardar")

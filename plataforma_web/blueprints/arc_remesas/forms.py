"""
Archivo - Remesas, formularios
"""
from flask_wtf import FlaskForm
from flask_login import current_user
from datetime import date
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms import IntegerField, StringField, SubmitField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

from plataforma_web.blueprints.arc_remesas.models import ArcRemesa
from plataforma_web.blueprints.arc_remesas_documentos.models import ArcRemesaDocumento


def remesas_opciones():
    """Distrito: opciones para select"""
    return ArcRemesa.query.filter_by(autoridad_id=current_user.autoridad.id).filter_by(estado="PENDIENTE").filter_by(estatus="A").order_by(ArcRemesa.anio).all()


class ArcRemesaNewForm(FlaskForm):
    """Formulario nueva Remesa"""

    num_oficio = StringField("Núm. Oficio", validators=[Optional(), Length(max=16)])
    anio = IntegerField("Año", validators=[DataRequired(), NumberRange(1950, date.today().year)])
    crear = SubmitField("Crear")


class ArcRemesaAddDocumentForm(FlaskForm):
    """Formulario para añadir un documento a una Remesa"""

    fojas = IntegerField("Fojas", validators=[Optional()])
    tipo = SelectField("Tipo", choices=ArcRemesaDocumento.TIPOS, validators=[DataRequired()])
    observaciones = TextAreaField("Observaciones", validators=[Optional(), Length(max=256)])
    tiene_anomalia = BooleanField("Tiene Anomalía", validators=[Optional()])
    remesas = QuerySelectField("Remesa", query_factory=remesas_opciones, get_label="anio", validators=[DataRequired()])
    agregar = SubmitField("Agregar Documento")


class ArcRemesaAsignationForm(FlaskForm):
    """Formulario Asignación"""

    asignado = SelectField("Archivista", coerce=int, validate_choice=False, validators=[Optional()])
    asignar = SubmitField("Asignar")


class ArcRemesaRefuseForm(FlaskForm):
    """Formulario Rechazo"""

    observaciones = TextAreaField("Observaciones", validators=[DataRequired(), Length(max=256)])
    rechazar = SubmitField("Rechazar")

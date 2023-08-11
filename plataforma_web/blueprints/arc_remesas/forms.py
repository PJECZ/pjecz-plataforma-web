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


class ArcRemesaNewForm(FlaskForm):
    """Formulario nueva Remesa"""

    num_oficio = StringField("Núm. Oficio", validators=[Optional(), Length(max=16)])
    anio = IntegerField("Año", validators=[DataRequired(), NumberRange(1900, date.today().year)])
    tipo_documentos = SelectField("Tipo de Documentos", choices=ArcRemesa.TIPOS_DOCUMENTOS, validators=[DataRequired()])
    crear = SubmitField("Crear")


class ArcRemesaEditForm(FlaskForm):
    """Formulario para editar Remesa"""

    # campos de solo lectura
    creado_readonly = StringField("Creado")
    juzgado_readonly = StringField("Instancia")
    tipo_documentos_readonly = StringField("Tipo de Documentos")
    # campos actualizables
    anio = IntegerField("Año", validators=[DataRequired(), NumberRange(1900, date.today().year)])
    num_oficio = StringField("Núm. Oficio", validators=[Optional(), Length(max=16)])
    observaciones = TextAreaField("Observaciones", validators=[Optional(), Length(max=256)])
    guardar = SubmitField("Guardar")


class ArcRemesaAddDocumentForm(FlaskForm):
    """Formulario para añadir un documento a una Remesa"""

    remesas = SelectField("Remesa", coerce=int, validate_choice=False, validators=[DataRequired()])
    fojas = IntegerField("Fojas", validators=[DataRequired()])
    tipo_juzgado = SelectField("Tipo de Instancia", choices=ArcRemesaDocumento.TIPOS, validators=[DataRequired()])
    observaciones = TextAreaField("Observaciones", validators=[Optional(), Length(max=256)])
    agregar = SubmitField("Agregar Documento")


class ArcRemesaAsignationForm(FlaskForm):
    """Formulario Asignación"""

    asignado = SelectField("Archivista", coerce=int, validate_choice=False, validators=[Optional()])
    asignar = SubmitField("Asignar")


class ArcRemesaRefuseForm(FlaskForm):
    """Formulario Rechazo"""

    observaciones = TextAreaField("Observaciones", validators=[DataRequired(), Length(max=256)])
    rechazar = SubmitField("Rechazar")

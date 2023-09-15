"""
Archivo - Remesas, formularios
"""
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import IntegerField, StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional, Length

from plataforma_web.blueprints.arc_remesas_documentos.models import ArcRemesaDocumento
from plataforma_web.blueprints.arc_remesas.models import ArcRemesa


class ArcRemesaNewForm(FlaskForm):
    """Formulario nueva Remesa"""

    num_oficio = StringField("Núm. Oficio: (núm/año)", validators=[DataRequired(), Length(max=16)])
    anio = StringField("Años: (Años de inicio - Año final)", validators=[DataRequired()])
    tipo_documentos = SelectField("Tipo de Documentos", coerce=int, validate_choice=False, validators=[DataRequired()])
    crear = SubmitField("Crear")


class ArcRemesaEditForm(FlaskForm):
    """Formulario para editar Remesa"""

    # campos de solo lectura
    creado_readonly = StringField("Creado")
    juzgado_readonly = StringField("Instancia")
    tipo_documentos_readonly = StringField("Tipo de Documentos")
    # campos actualizables
    anio = StringField("Años: (Años de inicio - Año final)", validators=[DataRequired()])
    num_oficio = StringField("Núm. Oficio: (núm/año)", validators=[DataRequired(), Length(max=16)])
    observaciones_solicitante = TextAreaField("Observaciones del Solicitante", validators=[Optional(), Length(max=256)])
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

    anomalia_general = SelectField("Anomalía General", choices=ArcRemesa.ANOMALIAS, validators=[DataRequired()])
    observaciones_archivista = TextAreaField("Observaciones por parte de Archivo", validators=[Optional(), Length(max=256)])
    rechazar = SubmitField("Rechazar")


class ArcRemesaAnomaliaForm(FlaskForm):
    """Formulario Rechazo"""

    anomalia_general = SelectField("Anomalía General", choices=ArcRemesa.ANOMALIAS, validators=[DataRequired()])
    observaciones_archivista = TextAreaField("Observaciones por parte de Archivo", validators=[Optional(), Length(max=256)])
    guardar = SubmitField("Guardar")
    eliminar = SubmitField("Eliminar")

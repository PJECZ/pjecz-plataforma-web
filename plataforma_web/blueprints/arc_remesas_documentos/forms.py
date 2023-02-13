"""
Archivo - Documentos anexos en Remesas, formularios
"""
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional, Length

from plataforma_web.blueprints.arc_remesas_documentos.models import ArcRemesaDocumento


class ArcRemesaDocumentoEditForm(FlaskForm):
    """Formulario para editar Documento anexo en Remesa"""

    fojas = IntegerField("Fojas", validators=[DataRequired()])
    tipo_juzgado = SelectField("Tipo de Juzgado", choices=ArcRemesaDocumento.TIPOS, validators=[DataRequired()])
    observaciones = TextAreaField("Observaciones", validators=[Optional(), Length(max=256)])
    guardar = SubmitField("Guardar")


class ArcRemesaDocumentoArchiveForm(FlaskForm):
    """Formulario para archivar Documento anexo en Remesa"""

    fojas = IntegerField("Fojas", validators=[DataRequired()])
    observaciones = TextAreaField("Observaciones", validators=[Optional(), Length(max=256)])
    archivar = SubmitField("Archivar")

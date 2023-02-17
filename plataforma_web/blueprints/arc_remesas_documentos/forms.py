"""
Archivo - Documentos anexos en Remesas, formularios
"""
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.arc_remesas_documentos.models import ArcRemesaDocumento


def anomalias_tipos():
    anomalias = ArcRemesaDocumento.ANOMALIAS
    anomalias.update({"": ""})
    anomalias.move_to_end("", last=False)
    return anomalias


class ArcRemesaDocumentoEditForm(FlaskForm):
    """Formulario para editar Documento anexo en Remesa"""

    fojas = IntegerField("Fojas", validators=[DataRequired()])
    tipo_juzgado = SelectField("Tipo de Juzgado", choices=ArcRemesaDocumento.TIPOS, validators=[DataRequired()])
    observaciones_solicitante = TextAreaField("Observaciones", validators=[Optional(), Length(max=256)])
    guardar = SubmitField("Guardar")


class ArcRemesaDocumentoArchiveForm(FlaskForm):
    """Formulario para archivar Documento anexo en Remesa"""

    fojas = IntegerField("Fojas", validators=[Optional()])
    anomalia = SelectField("Anomalía", validators=[Optional()], choices=anomalias_tipos())
    observaciones_archivo = TextAreaField("Observaciones", validators=[Optional(), Length(max=256)])
    archivar = SubmitField("Archivar")

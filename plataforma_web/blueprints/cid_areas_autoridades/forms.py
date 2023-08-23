"""
CID Areas Autoridades, formularios
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from plataforma_web.blueprints.cid_areas.models import CIDArea

def cid_area_opciones():
    """CIDArea: opciones para select"""
    return CIDArea.query.filter_by(estatus="A").order_by(CIDArea.nombre).all()



class CIDAreaAutoridadForm(FlaskForm):
    """ Formulario CIDAreaAutoridad """
    autoridad = StringField('Autoridad', validators=[DataRequired()])
    cid_area = QuerySelectField(query_factory=cid_area_opciones, get_label="nombre", validators=[DataRequired()])
    descripcion = StringField('Descripción', validators=[DataRequired(), Length(max=256)])
    guardar = SubmitField('Guardar')

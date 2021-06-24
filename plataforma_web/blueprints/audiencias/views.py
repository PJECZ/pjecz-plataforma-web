"""
Audiencias, vistas
"""
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from lib.safe_string import safe_expediente, safe_message

from plataforma_web.blueprints.roles.models import Permiso
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.audiencias.models import Audiencia
from plataforma_web.blueprints.audiencias.forms import AudienciaMCFMLDSTForm, AudienciaMAPOForm, AudienciaDPYSPForm

audiencias = Blueprint("audiencias", __name__, template_folder="templates")

MODULO = "AUDIENCIAS"
LIMITE_CONSULTAS = 400


@audiencias.before_request
@login_required
@permission_required(Permiso.VER_JUSTICIABLES)
def before_request():
    """Permiso por defecto"""


@audiencias.route("/audiencias")
def list_active():
    """Listado de Audiencias activos"""
    # Si es administrador, ve las audiencias de todas las autoridades
    if current_user.can_admin("audiencias"):
        audiencias_activas = Audiencia.query.filter(Audiencia.estatus == "A").order_by(Audiencia.creado.desc()).limit(LIMITE_CONSULTAS).all()
        return render_template("audiencias/list_admin.jinja2", audiencias=audiencias_activas, estatus="A")
    # No es administrador, consultar su autoridad
    if current_user.autoridad.es_jurisdiccional:
        sus_audiencias_activas = Audiencia.query.filter(Audiencia.autoridad == current_user.autoridad).filter(Audiencia.estatus == "A").order_by(Audiencia.creado.desc()).limit(LIMITE_CONSULTAS).all()
        return render_template("audiencias/list.jinja2", autoridad=current_user.autoridad, audiencias=sus_audiencias_activas, estatus="A")
    # No es jurisdiccional, se redirige al listado de distritos
    return redirect(url_for("audiencias.list_distritos"))


@audiencias.route("/audiencias/inactivos")
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def list_inactive():
    """Listado de Audiencias inactivos"""
    # Si es administrador, ve las audiencias de todas las autoridades
    if current_user.can_admin("audiencias"):
        audiencias_inactivas = Audiencia.query.filter(Audiencia.estatus == "B").order_by(Audiencia.creado.desc()).limit(LIMITE_CONSULTAS).all()
        return render_template("audiencias/list_admin.jinja2", audiencias=audiencias_inactivas, estatus="B")
    # No es administrador, consultar su autoridad
    if current_user.autoridad.es_jurisdiccional:
        sus_audiencias_inactivas = Audiencia.query.filter(Audiencia.autoridad == current_user.autoridad).filter(Audiencia.estatus == "B").order_by(Audiencia.creado.desc()).limit(LIMITE_CONSULTAS).all()
        return render_template("audiencias/list.jinja2", autoridad=current_user.autoridad, audiencias=sus_audiencias_inactivas, estatus="B")
    # No es jurisdiccional, se redirige al listado de distritos
    return redirect(url_for("audiencias.list_distritos"))


@audiencias.route("/audiencias/distritos")
def list_distritos():
    """Listado de Distritos"""
    distritos = Distrito.query.filter(Distrito.es_distrito_judicial == True).filter(Distrito.estatus == "A").order_by(Distrito.nombre).all()
    return render_template("audiencias/list_distritos.jinja2", distritos=distritos)


@audiencias.route("/audiencias/distrito/<int:distrito_id>")
def list_autoridades(distrito_id):
    """Listado de Autoridades de un distrito"""
    distrito = Distrito.query.get_or_404(distrito_id)
    autoridades = Autoridad.query.filter(Autoridad.distrito == distrito).filter(Autoridad.audiencia_categoria != "NO DEFINIDO").filter(Autoridad.estatus == "A").order_by(Autoridad.clave).all()
    return render_template("audiencias/list_autoridades.jinja2", distrito=distrito, autoridades=autoridades)


@audiencias.route("/audiencias/autoridad/<int:autoridad_id>")
def list_autoridad_audiencias(autoridad_id):
    """Listado de Audiencias activas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    audiencias_activas = Audiencia.query.filter(Audiencia.autoridad == autoridad).filter(Audiencia.estatus == "A").order_by(Audiencia.creado.desc()).limit(LIMITE_CONSULTAS).all()
    return render_template("audiencias/list.jinja2", autoridad=autoridad, audiencias=audiencias_activas, estatus="A")


@audiencias.route("/audiencias/inactivos/autoridad/<int:autoridad_id>")
@permission_required(Permiso.ADMINISTRAR_JUSTICIABLES)
def list_autoridad_audiencias_inactive(autoridad_id):
    """Listado de Audiencias inactivas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    audiencias_inactivas = Audiencia.query.filter(Audiencia.autoridad == autoridad).filter(Audiencia.estatus == "B").order_by(Audiencia.creado.desc()).limit(LIMITE_CONSULTAS).all()
    return render_template("audiencias/list.jinja2", autoridad=autoridad, audiencias=audiencias_inactivas, estatus="B")


@audiencias.route("/audiencias/<int:audiencia_id>")
def detail(audiencia_id):
    """Detalle de una Audiencia"""
    audiencia = Audiencia.query.get_or_404(audiencia_id)
    return render_template("audiencias/detail.jinja2", audiencia=audiencia)


@audiencias.route("/audiencias/nuevo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_JUSTICIABLES)
def new():
    """Nueva Audiencia"""

    # Validar autoridad
    autoridad = current_user.autoridad
    if autoridad is None or autoridad.estatus != "A":
        flash("El juzgado/autoridad no existe o no es activa.", "warning")
        return redirect(url_for("audiencias.list_active"))
    if autoridad.audiencia_categoria != 'MATERIAS C F M L D(CYF) SALAS (CYF) TCYA':
        flash("El juzgado/autoridad no tiena la categoría de audiencias correcta.", "warning")
        return redirect(url_for("audiencias.list_active"))

    # Si viene el formulario
    form = AudienciaMCFMLDSTForm()
    if form.validate_on_submit():

        # Insertar registro
        audiencia = Audiencia(
            autoridad=autoridad,
            tipo_audiencia=form.tipo_audiencia.data,
            tiempo=form.tiempo.data,
        )
        audiencia.save()

        # Mostrar mensaje de éxito e ir al detalle
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message('Nueva audiencia registro con...'),
            url=url_for('audiencias.detail', audiencia_id=audiencia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, 'success')
        return redirect(bitacora.url)

    # Prellenado del formulario
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    return render_template("audiencias/new.jinja2", form=form)


@audiencias.route("/audiencias/nuevo/<int:autoridad_id>", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_JUSTICIABLES)
def new_for_autoridad(autoridad_id):
    """Nueva Audiencia para una autoridad dada"""

    # Validar autoridad
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if autoridad is None or autoridad.estatus != "A":
        flash("El juzgado/autoridad no existe o no es activa.", "warning")
        return redirect(url_for("audiencias.list_active"))
    if autoridad.audiencia_categoria != 'MATERIAS C F M L D(CYF) SALAS (CYF) TCYA':
        flash("El juzgado/autoridad no tiena la categoría de audiencias correcta.", "warning")
        return redirect(url_for("audiencias.list_active"))

    # Si viene el formulario
    form = AudienciaMCFMLDSTForm()
    if form.validate_on_submit():

        # Insertar registro
        audiencia = Audiencia(
            autoridad=autoridad,
            tipo_audiencia=form.tipo_audiencia.data,
            tiempo=form.tiempo.data,
        )
        audiencia.save()

        # Mostrar mensaje de éxito e ir al detalle
        bitacora = Bitacora(
            modulo=MODULO,
            usuario=current_user,
            descripcion=safe_message('Nueva audiencia registro con...'),
            url=url_for('audiencias.detail', audiencia_id=audiencia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, 'success')
        return redirect(bitacora.url)

    # Prellenado del formulario
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    return render_template("audiencias/new.jinja2", form=form)


@audiencias.route('/audiencias/edicion/<int:audiencia_id>', methods=['GET', 'POST'])
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def edit(audiencia_id):
    """ Editar Audiencia """
    audiencia = Audiencia.query.get_or_404(audiencia_id)
    form = AudienciaMCFMLDSTForm()
    if form.validate_on_submit():
        audiencia.tiempo = form.tiempo.data
        audiencia.save()
        flash(f'Audiencia {audiencia.tiempo} guardado.', 'success')
        return redirect(url_for('audiencias.detail', audiencia_id=audiencia.id))
    form.tiempo.data = audiencia.tiempo
    return render_template('audiencias/edit.jinja2', form=form, audiencia=audiencia)


@audiencias.route('/audiencias/eliminar/<int:audiencia_id>')
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def delete(audiencia_id):
    """ Eliminar Audiencia """
    audiencia = Audiencia.query.get_or_404(audiencia_id)
    if audiencia.estatus == 'A':
        audiencia.delete()
        flash(f'Audiencia {audiencia.tipo_audiencia} eliminado.', 'success')
    return redirect(url_for('audiencias.detail', audiencia_id=audiencia.id))


@audiencias.route('/audiencias/recuperar/<int:audiencia_id>')
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def recover(audiencia_id):
    """ Recuperar Audiencia """
    audiencia = Audiencia.query.get_or_404(audiencia_id)
    if audiencia.estatus == 'B':
        audiencia.recover()
        flash(f'Audiencia {audiencia.tipo_audiencia} recuperado.', 'success')
    return redirect(url_for('audiencias.detail', audiencia_id=audiencia.id))

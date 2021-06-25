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
from plataforma_web.blueprints.audiencias.forms import AudienciaGenericaForm, AudienciaMapoForm, AudienciaDipesapeForm

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


@audiencias.route("/audiencias/nuevo/generica", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_JUSTICIABLES)
def new_generica():
    """Nueva Audiencia Materias Mat. CFML, Dist. CyF, Salas CyF y TCyA"""

    # Validar autoridad
    autoridad = current_user.autoridad
    if autoridad is None or autoridad.estatus != "A":
        flash("El juzgado/autoridad no existe o no es activa.", "warning")
        return redirect(url_for("audiencias.list_active"))
    if autoridad.audiencia_categoria != "MAT(CFML) DIST(CYF) SALAS(CYF) TCYA":
        flash("La categoría de audiencia no es MAT(CFML) DIST(CYF) SALAS(CYF) TCYA.", "warning")
        return redirect(url_for("audiencias.list_active"))

    # Si viene el formulario
    form = AudienciaGenericaForm()
    if form.validate_on_submit():

        # Insertar registro
        audiencia = Audiencia(
            autoridad=autoridad,
            tiempo=form.tiempo.data,
            tipo_audiencia=form.tipo_audiencia.data,
            expediente=form.expediente.data,
            actores=form.actores.data,
            demandados=form.demandados.data,
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


@audiencias.route("/audiencias/nuevo/mapo", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_JUSTICIABLES)
def new_mapo():
    """Nueva Audiencia Materia Acusatorio Penal Oral"""

    # Validar autoridad
    autoridad = current_user.autoridad
    if autoridad is None or autoridad.estatus != "A":
        flash("El juzgado/autoridad no existe o no es activa.", "warning")
        return redirect(url_for("audiencias.list_active"))
    if autoridad.audiencia_categoria != "MATERIA ACUSATORIO PENAL ORAL":
        flash("La categoría de audiencia no es MATERIA ACUSATORIO PENAL ORAL.", "warning")
        return redirect(url_for("audiencias.list_active"))

    # Si viene el formulario
    form = AudienciaMapoForm()
    if form.validate_on_submit():

        # Insertar registro
        audiencia = Audiencia(
            autoridad=autoridad,
            tiempo=form.tiempo.data,
            tipo_audiencia=form.tipo_audiencia.data,
            sala=form.sala.data,
            caracter=form.caracter.data,
            causa_penal=form.causa_penal.data,
            delitos=form.delitos.data,
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


@audiencias.route("/audiencias/nuevo/dipesape", methods=["GET", "POST"])
@permission_required(Permiso.CREAR_JUSTICIABLES)
def new_dipesape():
    """Nueva Audiencia Distritales Penales y Salas Penales"""

    # Validar autoridad
    autoridad = current_user.autoridad
    if autoridad is None or autoridad.estatus != "A":
        flash("El juzgado/autoridad no existe o no es activa.", "warning")
        return redirect(url_for("audiencias.list_active"))
    if autoridad.audiencia_categoria != "DISTRITALES PENALES Y SALAS PENALES":
        flash("La categoría de audiencia no es DISTRITALES PENALES Y SALAS PENALES.", "warning")
        return redirect(url_for("audiencias.list_active"))

    # Si viene el formulario
    form = AudienciaDipesapeForm()
    if form.validate_on_submit():

        # Insertar registro
        audiencia = Audiencia(
            autoridad=autoridad,
            tiempo=form.tiempo.data,
            tipo_audiencia=form.tipo_audiencia.data,
            toca=form.toca.data,
            expediente_origen=form.expediente_origen.data,
            delitos=form.delitos.data,
            imputados=form.imputados.data,
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


def edit_success(audiencia):
    """Mensaje de éxito al editar una audiencia"""
    bitacora = Bitacora(
        modulo=MODULO,
        usuario=current_user,
        descripcion=safe_message(f'Editada la audiencia {audiencia.tipo_audiencia} de {audiencia.autoridad.clave}.'),
        url=url_for('audiencias.detail', audiencia_id=audiencia.id),
    )
    bitacora.save()
    return bitacora


@audiencias.route('/audiencias/edicion/generica/<int:audiencia_id>', methods=['GET', 'POST'])
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def edit_generica(audiencia_id):
    """Editar Audiencia Materias Mat. CFML, Dist. CyF, Salas CyF y TCyA"""

    # Validar autoridad
    autoridad = current_user.autoridad
    if autoridad is None or autoridad.estatus != "A":
        flash("El juzgado/autoridad no existe o no es activa.", "warning")
        return redirect(url_for("audiencias.list_active"))
    if autoridad.audiencia_categoria != "MAT(CFML) DIST(CYF) SALAS(CYF) TCYA":
        flash("La categoría de audiencia no es MAT(CFML) DIST(CYF) SALAS(CYF) TCYA.", "warning")
        return redirect(url_for("audiencias.list_active"))

    # Cargar audiencia
    audiencia = Audiencia.query.get_or_404(audiencia_id)

    # Si viene el formulario
    form = AudienciaGenericaForm()
    if form.validate_on_submit():

        # Actualizar registro
        audiencia.tiempo = form.tiempo.data
        audiencia.tipo_audiencia = form.tipo_audiencia.data
        audiencia.expediente = form.expediente.data
        audiencia.actores = form.actores.data
        audiencia.demandados = form.demandados.data
        audiencia.save()

        # Registrar en bitácora e ir al detalle
        bitacora = edit_success(audiencia)
        flash(bitacora.descripcion, 'success')
        return redirect(bitacora.url)

    # Prellenado del formulario
    form.tiempo.data = audiencia.tiempo
    return render_template('audiencias/edit.jinja2', form=form, audiencia=audiencia)


@audiencias.route('/audiencias/edicion/mapo/<int:audiencia_id>', methods=['GET', 'POST'])
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def edit_mapo(audiencia_id):
    """Editar Audiencia Materia Acusatorio Penal Oral"""

    # Validar autoridad
    autoridad = current_user.autoridad
    if autoridad is None or autoridad.estatus != "A":
        flash("El juzgado/autoridad no existe o no es activa.", "warning")
        return redirect(url_for("audiencias.list_active"))
    if autoridad.audiencia_categoria != "MATERIA ACUSATORIO PENAL ORAL":
        flash("La categoría de audiencia no es MATERIA ACUSATORIO PENAL ORAL.", "warning")
        return redirect(url_for("audiencias.list_active"))

    # Cargar audiencia
    audiencia = Audiencia.query.get_or_404(audiencia_id)

    # Si viene el formulario
    form = AudienciaMapoForm()
    if form.validate_on_submit():

        # Actualizar registro
        audiencia.tiempo = form.tiempo.data
        audiencia.tipo_audiencia = form.tipo_audiencia.data
        audiencia.sala = form.sala.data
        audiencia.caracter = form.caracter.data
        audiencia.causa_penal = form.causa_penal.data
        audiencia.delitos = form.delitos.data
        audiencia.save()

        # Registrar en bitácora e ir al detalle
        bitacora = edit_success(audiencia)
        flash(bitacora.descripcion, 'success')
        return redirect(bitacora.url)

    # Prellenado del formulario
    form.tiempo.data = audiencia.tiempo
    return render_template('audiencias/edit.jinja2', form=form, audiencia=audiencia)


@audiencias.route('/audiencias/edicion/<int:audiencia_id>', methods=['GET', 'POST'])
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def edit_dipesape(audiencia_id):
    """Editar Audiencia Distritales Penales y Salas Penales"""

    # Validar autoridad
    autoridad = current_user.autoridad
    if autoridad is None or autoridad.estatus != "A":
        flash("El juzgado/autoridad no existe o no es activa.", "warning")
        return redirect(url_for("audiencias.list_active"))
    if autoridad.audiencia_categoria != "DISTRITALES PENALES Y SALAS PENALES":
        flash("La categoría de audiencia no es DISTRITALES PENALES Y SALAS PENALES.", "warning")
        return redirect(url_for("audiencias.list_active"))

    # Cargar audiencia
    audiencia = Audiencia.query.get_or_404(audiencia_id)

    # Si viene el formulario
    form = AudienciaDipesapeForm()
    if form.validate_on_submit():

        # Actualizar registro
        audiencia.tiempo = form.tiempo.data
        audiencia.tipo_audiencia = form.tipo_audiencia.data
        audiencia.toca = form.toca.data
        audiencia.expediente_origen = form.expediente_origen.data
        audiencia.delitos = form.delitos.data
        audiencia.imputados = form.imputados.data
        audiencia.save()

        # Registrar en bitácora e ir al detalle
        bitacora = edit_success(audiencia)
        flash(bitacora.descripcion, 'success')
        return redirect(bitacora.url)

    # Prellenado del formulario
    form.tiempo.data = audiencia.tiempo
    return render_template('audiencias/edit.jinja2', form=form, audiencia=audiencia)


def delete_success(audiencia):
    """Mensaje de éxito al eliminar una audiencia"""
    bitacora = Bitacora(
        modulo=MODULO,
        usuario=current_user,
        descripcion=safe_message(f'Eliminada la audiencia {audiencia.tipo_audiencia} de {audiencia.autoridad.clave}.'),
        url=url_for('audiencias.detail', audiencia_id=audiencia.id),
    )
    bitacora.save()
    return bitacora


@audiencias.route('/audiencias/eliminar/<int:audiencia_id>')
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def delete(audiencia_id):
    """ Eliminar Audiencia """
    audiencia = Audiencia.query.get_or_404(audiencia_id)
    if audiencia.estatus == 'A':
        if current_user.can_admin("audiencias") or current_user.autoridad_id == audiencia.autoridad_id:
            audiencia.delete()
            bitacora = delete_success(audiencia)
            flash(bitacora.descripcion, 'success')
        else:
            flash("No tiene permiso para eliminar.", "warning")
    return redirect(url_for('audiencias.detail', audiencia_id=audiencia.id))


def recover_success(audiencia):
    """Mensaje de éxito al recuperar una audiencia"""
    bitacora = Bitacora(
        modulo=MODULO,
        usuario=current_user,
        descripcion=safe_message(f'Recuperada la audiencia {audiencia.tipo_audiencia} de {audiencia.autoridad.clave}.'),
        url=url_for('audiencias.detail', audiencia_id=audiencia.id),
    )
    bitacora.save()
    return bitacora


@audiencias.route('/audiencias/recuperar/<int:audiencia_id>')
@permission_required(Permiso.MODIFICAR_JUSTICIABLES)
def recover(audiencia_id):
    """ Recuperar Audiencia """
    audiencia = Audiencia.query.get_or_404(audiencia_id)
    if audiencia.estatus == 'B':
        if current_user.can_admin("audiencias") or current_user.autoridad_id == audiencia.autoridad_id:
            audiencia.recover()
            bitacora = recover_success(audiencia)
            flash(bitacora.descripcion, 'success')
        else:
            flash("No tiene permiso para eliminar.", "warning")
    return redirect(url_for('audiencias.detail', audiencia_id=audiencia.id))

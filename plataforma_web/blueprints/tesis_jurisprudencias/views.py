"""
Tesis y Jurisprudencias, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib import datatables
from lib.safe_string import safe_string, safe_message
from lib.time_utc import combine_to_utc, decombine_to_local
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.tesis_jurisprudencias.models import TesisJurisprudencia
from plataforma_web.blueprints.tesis_jurisprudencias.forms import TesisJurisprudenciaForm

MODULO = "TESIS JURISPRUDENCIAS"
ORGANOS_JURISDICCIONALES = ["PLENO O SALA DEL TSJ", "TRIBUNAL DISTRITAL", "TRIBUNAL DE CONCILIACION Y ARBITRAJE"]

tesis_jurisprudencias = Blueprint("tesis_jurisprudencias", __name__, template_folder="templates")


@tesis_jurisprudencias.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@tesis_jurisprudencias.route("/tesis_jurisprudencias")
def list_active():
    """Listado de Tesis Jurisprudencias activos"""
    # Si es administrador ve todo
    if current_user.can_admin(MODULO):
        return render_template(
            "tesis_jurisprudencias/list_admin.jinja2",
            autoridad=None,
            filtros=json.dumps({"estatus": "A"}),
            titulo="Todas las Tesis y Jurisprudencias",
            estatus="A",
        )
    # Si puede editar o crear glosas ve lo de su autoridad
    if current_user.can_edit(MODULO) or current_user.can_insert(MODULO):
        autoridad = current_user.autoridad
        return render_template(
            "tesis_jurisprudencias/list.jinja2",
            autoridad=autoridad,
            filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "A"}),
            titulo=f"Tesis y Jurisprudencias de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
            estatus="A",
        )
    # Ninguno de los anteriores
    return render_template(
        "tesis_jurisprudencias/list.jinja2",
        autoridad=None,
        filtros=json.dumps({"estatus": "A"}),
        titulo="Todas las Tesis y Jurisprudencias",
        estatus="A",
    )


@tesis_jurisprudencias.route("/tesis_jurisprudencias/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    # Si es administrador ve todo
    if current_user.can_admin(MODULO):
        return render_template(
            "tesis_jurisprudencias/list_admin.jinja2",
            autoridad=None,
            filtros=json.dumps({"estatus": "B"}),
            titulo="Todas las Tesis y Jurisprudencias inactivas",
            estatus="B",
        )
    # Si puede editar o crear glosas ve lo de su autoridad
    if current_user.can_edit(MODULO) or current_user.can_insert(MODULO):
        autoridad = current_user.autoridad
        return render_template(
            "tesis_jurisprudencias/list.jinja2",
            autoridad=autoridad,
            filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "B"}),
            titulo=f"Tesis y Jurisprudencias inactivas de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
            estatus="B",
        )
    # Ninguno de los anteriores
    return render_template(
        "tesis_jurisprudencias/list.jinja2",
        autoridad=None,
        filtros=json.dumps({"estatus": "B"}),
        titulo="Todas las Tesis Jurisprudencias inactivas",
        estatus="B",
    )


@tesis_jurisprudencias.route("/tesis_jurisprudencias/autoridades")
def list_autoridades():
    """Listado de Autoridades"""
    autoridades = Autoridad.query.filter(Autoridad.organo_jurisdiccional.in_(ORGANOS_JURISDICCIONALES)).filter_by(estatus="A").order_by(Autoridad.clave).all()
    return render_template("tesis_jurisprudencias/list_autoridades.jinja2", autoridades=autoridades)


@tesis_jurisprudencias.route("/tesis_jurisprudencias/autoridad/<int:autoridad_id>")
def list_autoridad_tesis_jurisprudencias(autoridad_id):
    """Listado de Tesis Jurisprudencias activas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if current_user.can_admin(MODULO):
        plantilla = "tesis_jurisprudencias/list_admin.jinja2"
    else:
        plantilla = "tesis_jurisprudencias/list.jinja2"
    return render_template(
        plantilla,
        autoridad=autoridad,
        filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "A"}),
        titulo=f"Tesis Jurisprudencias de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
        estatus="A",
    )


@tesis_jurisprudencias.route("/tesis_jurisprudencias/inactivos/autoridad/<int:autoridad_id>")
def list_autoridad_tesis_jurisprudencias_inactive(autoridad_id):
    """Listado de Tesis Jurisprudencias activas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if current_user.can_admin(MODULO):
        plantilla = "tesis_jurisprudencias/list_admin.jinja2"
    else:
        plantilla = "tesis_jurisprudencias/list.jinja2"
    return render_template(
        plantilla,
        autoridad=autoridad,
        filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "A"}),
        titulo=f"Tesis Jurisprudencias inactivas de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
        estatus="B",
    )


@tesis_jurisprudencias.route("/tesis_jurisprudencias/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Tesis Jurisprudencias"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = TesisJurisprudencia.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(TesisJurisprudencia.titulo).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "titulo": resultado.titulo,
                    "url": url_for("tesis_jurisprudencias.detail", tesis_jurisprudencia_id=resultado.id),
                },
                "clase": resultado.clase,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@tesis_jurisprudencias.route("/tesis_jurisprudencias/datatable_json_admin", methods=["GET", "POST"])
def datatable_json_admin():
    """DataTable JSON para listado de Tesis Jurisprudencias admin"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = TesisJurisprudencia.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    registros = consulta.order_by(TesisJurisprudencia.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "creado": resultado.creado.strftime("%Y-%m-%d %H:%M:%S"),
                "autoridad_clave": resultado.autoridad.clave,
                "detalle": {
                    "titulo": resultado.titulo,
                    "url": url_for("tesis_jurisprudencias.detail", tesis_jurisprudencia_id=resultado.id),
                },
                "clase": resultado.clase,
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@tesis_jurisprudencias.route("/tesis_jurisprudencias/<int:tesis_jurisprudencia_id>")
def detail(tesis_jurisprudencia_id):
    """Detalle de una Tesis Jurisprudencias"""
    tesis_jurisprudencia = TesisJurisprudencia.query.get_or_404(tesis_jurisprudencia_id)
    return render_template("tesis_jurisprudencias/detail.jinja2", tesis_jurisprudencia=tesis_jurisprudencia)


@tesis_jurisprudencias.route("/tesis_jurisprudencias/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva Tesis Jurisprudencia como Juzgado"""
    # Validar autoridad
    autoridad = current_user.autoridad
    if autoridad is None or autoridad.estatus != "A":
        flash("El juzgado/autoridad no existe o no es activa.", "warning")
        return redirect(url_for("tesis_jurisprudencias.list_active"))
    if not autoridad.distrito.es_distrito_judicial:
        flash("El juzgado/autoridad no está en un distrito jurisdiccional.", "warning")
        return redirect(url_for("tesis_jurisprudencias.list_active"))
    if not autoridad.es_jurisdiccional:
        flash("El juzgado/autoridad no es jurisdiccional.", "warning")
        return redirect(url_for("tesis_jurisprudencias.list_active"))
    # Formulario
    form = TesisJurisprudenciaForm()
    if form.validate_on_submit():
        es_valido = True
        # Definir tiempo de publicación con fecha y horas:minutos
        try:
            publicacion_tiempo = combine_to_utc(form.publicacion_fecha.data, form.publicacion_horas_minutos.data)
        except ValueError as error:
            flash(str(error), "warning")
            es_valido = False
        # Definir tiempo de publicación con fecha y horas:minutos
        try:
            aplicacion_tiempo = combine_to_utc(form.aplicacion_fecha.data, form.aplicacion_horas_minutos.data)
        except ValueError as error:
            flash(str(error), "warning")
            es_valido = False
        # Guardar si es válido
        if es_valido:
            tesis_jurisprudencia = TesisJurisprudencia(
                titulo=safe_string(form.titulo.data),
                subtitulo=safe_string(form.subtitulo.data),
                autoridad=autoridad,
                epoca=form.epoca.data,
                materia=form.materia.data,
                tipo=form.tipo.data,
                estado=form.estado.data,
                clave_control=safe_string(form.clave_control.data),
                clase=form.clase.data,
                rubro=safe_string(form.rubro.data),
                texto=form.texto.data,
                precedentes=form.precedentes.data,
                votacion=safe_string(form.votacion.data),
                votos_particulares=safe_string(form.votos_particulares.data),
                aprobacion_fecha=form.aprobacion_fecha.data,
                publicacion_tiempo=publicacion_tiempo,
                aplicacion_tiempo=aplicacion_tiempo,
            )
            tesis_jurisprudencia.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nueva Tesis Jurisprudencia {tesis_jurisprudencia.titulo}"),
                url=url_for("tesis_jurisprudencias.detail", tesis_jurisprudencia_id=tesis_jurisprudencia.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    return render_template("tesis_jurisprudencias/new.jinja2", form=form)


@tesis_jurisprudencias.route("/tesis_jurisprudencias/nuevo/<int:autoridad_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.ADMINISTRAR)
def new_for_autoridad(autoridad_id):
    """Nueva Tesis Jurisprudencia como Administrador"""
    # Validar autoridad
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if autoridad is None or autoridad.estatus != "A":
        flash("El juzgado/autoridad no existe o no es activa.", "warning")
        return redirect(url_for("tesis_jurisprudencias.list_active"))
    if not autoridad.distrito.es_distrito_judicial:
        flash("El juzgado/autoridad no está en un distrito jurisdiccional.", "warning")
        return redirect(url_for("tesis_jurisprudencias.list_active"))
    if not autoridad.es_jurisdiccional:
        flash("El juzgado/autoridad no es jurisdiccional.", "warning")
        return redirect(url_for("tesis_jurisprudencias.list_active"))
    # Formulario
    form = TesisJurisprudenciaForm()
    if form.validate_on_submit():
        es_valido = True
        # Definir tiempo de publicación con fecha y horas:minutos
        try:
            publicacion_tiempo = combine_to_utc(form.publicacion_fecha.data, form.publicacion_horas_minutos.data)
        except ValueError as error:
            flash(str(error), "warning")
            es_valido = False
        # Definir tiempo de publicación con fecha y horas:minutos
        try:
            aplicacion_tiempo = combine_to_utc(form.aplicacion_fecha.data, form.aplicacion_horas_minutos.data)
        except ValueError as error:
            flash(str(error), "warning")
            es_valido = False
        # Guardar si es válido
        if es_valido:
            tesis_jurisprudencia = TesisJurisprudencia(
                titulo=safe_string(form.titulo.data),
                subtitulo=safe_string(form.subtitulo.data),
                autoridad=autoridad,
                epoca=form.epoca.data,
                materia=form.materia.data,
                tipo=form.tipo.data,
                estado=form.estado.data,
                clave_control=safe_string(form.clave_control.data),
                clase=form.clase.data,
                rubro=safe_string(form.rubro.data),
                texto=form.texto.data,
                precedentes=form.precedentes.data,
                votacion=safe_string(form.votacion.data),
                votos_particulares=safe_string(form.votos_particulares.data),
                aprobacion_fecha=form.aprobacion_fecha.data,
                publicacion_tiempo=publicacion_tiempo,
                aplicacion_tiempo=aplicacion_tiempo,
            )
            tesis_jurisprudencia.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nueva Tesis Jurisprudencia {tesis_jurisprudencia.titulo}"),
                url=url_for("tesis_jurisprudencias.detail", tesis_jurisprudencia_id=tesis_jurisprudencia.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    return render_template(
        "tesis_jurisprudencias/new_for_autoridad.jinja2",
        form=form,
        autoridad=autoridad,
    )


@tesis_jurisprudencias.route("/tesis_jurisprudencias/edicion/<int:tesis_jurisprudencia_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(tesis_jurisprudencia_id):
    """Editar Tesis Jurisprudencia como Juzgado"""
    tesis_jurisprudencia = TesisJurisprudencia.query.get_or_404(tesis_jurisprudencia_id)
    form = TesisJurisprudenciaForm()
    if form.validate_on_submit():
        es_valido = True
        # Definir tiempo de publicación con fecha y horas:minutos
        try:
            publicacion_tiempo = combine_to_utc(form.publicacion_fecha.data, form.publicacion_horas_minutos.data)
        except ValueError as error:
            flash(str(error), "warning")
            es_valido = False
        # Definir tiempo de publicación con fecha y horas:minutos
        try:
            aplicacion_tiempo = combine_to_utc(form.aplicacion_fecha.data, form.aplicacion_horas_minutos.data)
        except ValueError as error:
            flash(str(error), "warning")
            es_valido = False
        # Guardar si es válido
        if es_valido:
            tesis_jurisprudencia.titulo = safe_string(form.titulo.data)
            tesis_jurisprudencia.subtitulo = safe_string(form.subtitulo.data)
            tesis_jurisprudencia.epoca = form.epoca.data
            tesis_jurisprudencia.materia = form.materia.data
            tesis_jurisprudencia.tipo = form.tipo.data
            tesis_jurisprudencia.estado = form.estado.data
            tesis_jurisprudencia.clave_control = safe_string(form.clave_control.data)
            tesis_jurisprudencia.clase = form.clase.data
            tesis_jurisprudencia.rubro = safe_string(form.rubro.data)
            tesis_jurisprudencia.texto = form.texto.data
            tesis_jurisprudencia.precedentes = form.precedentes.data
            tesis_jurisprudencia.votacion = safe_string(form.votacion.data)
            tesis_jurisprudencia.votos_particulares = safe_string(form.votos_particulares.data)
            tesis_jurisprudencia.aprobacion_fecha = form.aprobacion_fecha.data
            tesis_jurisprudencia.publicacion_tiempo = publicacion_tiempo
            tesis_jurisprudencia.aplicacion_tiempo = aplicacion_tiempo
            tesis_jurisprudencia.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editado Tesis Jurisprudencia {tesis_jurisprudencia.titulo}"),
                url=url_for("tesis_jurisprudencias.detail", tesis_jurisprudencia_id=tesis_jurisprudencia.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
    form.titulo.data = tesis_jurisprudencia.titulo
    form.subtitulo.data = tesis_jurisprudencia.subtitulo
    form.epoca.data = tesis_jurisprudencia.epoca
    form.materia.data = tesis_jurisprudencia.materia
    form.tipo.data = tesis_jurisprudencia.tipo
    form.estado.data = tesis_jurisprudencia.estado
    form.clave_control.data = tesis_jurisprudencia.clave_control
    form.clase.data = tesis_jurisprudencia.clase
    form.rubro.data = tesis_jurisprudencia.rubro
    form.texto.data = tesis_jurisprudencia.texto
    form.precedentes.data = tesis_jurisprudencia.precedentes
    form.votacion.data = tesis_jurisprudencia.votacion
    form.votos_particulares.data = tesis_jurisprudencia.votos_particulares
    form.aprobacion_fecha.data = tesis_jurisprudencia.aprobacion_fecha
    form.publicacion_fecha.data, form.publicacion_horas_minutos.data = decombine_to_local(tesis_jurisprudencia.publicacion_tiempo)
    form.aplicacion_fecha.data, form.aplicacion_horas_minutos.data = decombine_to_local(tesis_jurisprudencia.aplicacion_tiempo)
    return render_template("tesis_jurisprudencias/edit.jinja2", form=form, tesis_jurisprudencia=tesis_jurisprudencia)


@tesis_jurisprudencias.route("/tesis_jurisprudencias/eliminar/<int:tesis_jurisprudencia_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(tesis_jurisprudencia_id):
    """Eliminar Tesis Jurisprudencia como Juzgado"""
    tesis_jurisprudencia = TesisJurisprudencia.query.get_or_404(tesis_jurisprudencia_id)
    if tesis_jurisprudencia.estatus == "A":
        if current_user.can_admin(MODULO) or current_user.autoridad_id == tesis_jurisprudencia.autoridad_id:
            tesis_jurisprudencia.delete()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Eliminado Tesis Jurisprudencia {tesis_jurisprudencia.titulo}"),
                url=url_for("tesis_jurisprudencias.detail", tesis_jurisprudencia_id=tesis_jurisprudencia.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
    return redirect(url_for("tesis_jurisprudencias.detail", tesis_jurisprudencia_id=tesis_jurisprudencia.id))


@tesis_jurisprudencias.route("/tesis_jurisprudencias/recuperar/<int:tesis_jurisprudencia_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(tesis_jurisprudencia_id):
    """Recuperar Tesis Jurisprudencia como Juzgado"""
    tesis_jurisprudencia = TesisJurisprudencia.query.get_or_404(tesis_jurisprudencia_id)
    if tesis_jurisprudencia.estatus == "B":
        if current_user.can_admin(MODULO) or current_user.autoridad_id == tesis_jurisprudencia.autoridad_id:
            tesis_jurisprudencia.recover()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Recuperado Tesis {tesis_jurisprudencia.titulo}"),
                url=url_for("tesis_jurisprudencias.detail", tesis_jurisprudencia_id=tesis_jurisprudencia.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
    return redirect(url_for("tesis_jurisprudencias.detail", tesis_jurisprudencia_id=tesis_jurisprudencia.id))

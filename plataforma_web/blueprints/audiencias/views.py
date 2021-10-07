"""
Audiencias, vistas
"""
import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib import datatables
from lib.safe_string import safe_expediente, safe_message, safe_string
from lib.time_utc import combine_to_utc, decombine_to_local, join_for_message
from plataforma_web.blueprints.usuarios.decorators import permission_required

from plataforma_web.blueprints.audiencias.models import Audiencia
from plataforma_web.blueprints.audiencias.forms import AudienciaGenericaForm, AudienciaMapoForm, AudienciaDipeForm, AudienciaSapeForm
from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso

audiencias = Blueprint("audiencias", __name__, template_folder="templates")

MODULO = "AUDIENCIAS"


def plantilla_por_categoria(categoria: str, prefijo: str = "list_", sufijo: str = "", por_defecto: str = "list"):
    """Determinar la plantilla por tipo de agenda de audiencia"""
    if categoria == "CIVIL FAMILIAR MERCANTIL LETRADO TCYA":
        nombre = f"{prefijo}generica{sufijo}"
    elif categoria == "MATERIA ACUSATORIO PENAL ORAL":
        nombre = f"{prefijo}mapo{sufijo}"
    elif categoria == "DISTRITALES":
        nombre = f"{prefijo}dipe{sufijo}"
    elif categoria == "SALAS":
        nombre = f"{prefijo}sape{sufijo}"
    else:
        nombre = por_defecto
    return f"audiencias/{nombre}.jinja2"


@audiencias.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@audiencias.route("/audiencias")
def list_active():
    """Listado de Audiencias activos"""
    # Si es administrador ve todo
    if current_user.can_admin("AUDIENCIAS"):
        return render_template(
            "audiencias/list_admin.jinja2",
            autoridad=None,
            filtros=json.dumps({"estatus": "A"}),
            titulo="Todos las Audiencias",
            estatus="A",
        )
    # Si es jurisdiccional ve lo de su autoridad
    if current_user.autoridad.es_jurisdiccional:
        autoridad = current_user.autoridad
        return render_template(
            plantilla_por_categoria(autoridad.audiencia_categoria, por_defecto="list"),
            autoridad=autoridad,
            filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "A"}),
            titulo=f"Audiencias de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
            estatus="A",
        )
    # Ninguno de los anteriores
    return redirect(url_for("audiencias.list_distritos"))


@audiencias.route("/audiencias/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Audiencias inactivos"""
    # Si es administrador ve todo
    if current_user.can_admin("AUDIENCIAS"):
        return render_template(
            "audiencias/list_admin.jinja2",
            autoridad=None,
            filtros=json.dumps({"estatus": "B"}),
            titulo="Todos las Audiencias inactivos",
            estatus="B",
        )
    # Si es jurisdiccional ve lo de su autoridad
    if current_user.autoridad.es_jurisdiccional:
        autoridad = current_user.autoridad
        return render_template(
            plantilla_por_categoria(autoridad.audiencia_categoria, por_defecto="list"),
            autoridad=autoridad,
            filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "B"}),
            titulo=f"Audiencias inactivas de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
            estatus="B",
        )
    # Ninguno de los anteriores
    return redirect(url_for("audiencias.list_distritos"))


@audiencias.route("/audiencias/distritos")
def list_distritos():
    """Listado de Distritos"""
    return render_template(
        "audiencias/list_distritos.jinja2",
        distritos=Distrito.query.filter_by(es_distrito_judicial=True).filter_by(estatus="A").order_by(Distrito.nombre).all(),
    )


@audiencias.route("/audiencias/distrito/<int:distrito_id>")
def list_autoridades(distrito_id):
    """Listado de Autoridades de un distrito"""
    distrito = Distrito.query.get_or_404(distrito_id)
    return render_template(
        "audiencias/list_autoridades.jinja2",
        distrito=distrito,
        autoridades=Autoridad.query.filter(Autoridad.distrito == distrito).filter_by(es_jurisdiccional=True).filter_by(es_notaria=False).filter_by(estatus="A").order_by(Autoridad.clave).all(),
    )


@audiencias.route("/audiencias/autoridad/<int:autoridad_id>")
def list_autoridad_audiencias(autoridad_id):
    """Listado de Audiencias activas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if current_user.can_admin("AUDIENCIAS"):
        plantilla = plantilla_por_categoria(autoridad.audiencia_categoria, sufijo="_admin", por_defecto="list_admin")
    else:
        plantilla = plantilla_por_categoria(autoridad.audiencia_categoria, por_defecto="list")
    return render_template(
        plantilla,
        autoridad=autoridad,
        filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "A"}),
        titulo=f"Audiencias de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
        estatus="A",
    )


@audiencias.route("/audiencias/inactivos/autoridad/<int:autoridad_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_autoridad_audiencias_inactive(autoridad_id):
    """Listado de Audiencias inactivas de una autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if current_user.can_admin("AUDIENCIAS"):
        plantilla = plantilla_por_categoria(autoridad.audiencia_categoria, sufijo="_admin", por_defecto="list_admin")
    else:
        plantilla = plantilla_por_categoria(autoridad.audiencia_categoria, por_defecto="list")
    return render_template(
        plantilla,
        autoridad=autoridad,
        filtros=json.dumps({"autoridad_id": autoridad.id, "estatus": "B"}),
        titulo=f"Audiencias inactivas de {autoridad.distrito.nombre_corto}, {autoridad.descripcion_corta}",
        estatus="B",
    )


@audiencias.route("/audiencias/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de audiencias"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = datatables.get_parameters()
    # Consultar
    consulta = Audiencia.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "autoridad_id" in request.form:
        autoridad = Autoridad.query.get(request.form["autoridad_id"])
        if autoridad:
            consulta = consulta.filter_by(autoridad=autoridad)
    registros = consulta.order_by(Audiencia.tiempo.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for audiencia in registros:
        data.append(
            {
                "detalle": {
                    "tiempo": audiencia.tiempo,
                    "url": url_for("audiencias.detail", audiencia_id=audiencia.id),
                },
                "tipo_audiencia": audiencia.tipo_audiencia,
                "expediente": audiencia.expediente,
                "actores": audiencia.actores,
                "demandados": audiencia.demandados,
                "sala": audiencia.sala,
                "caracter": audiencia.caracter,
                "causa_penal": audiencia.causa_penal,
                "delitos": audiencia.delitos,
                "toca": audiencia.toca,
                "expediente_origen": audiencia.expediente_origen,
                "imputados": audiencia.imputados,
                "origen": audiencia.origen,
            }
        )
    # Entregar JSON
    return datatables.output(draw, total, data)


@audiencias.route("/audiencias/datatable_json_admin", methods=["GET", "POST"])
def datatable_json_admin():
    """DataTable JSON para listado de audiencias admin"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = datatables.get_parameters()
    # Consultar
    consulta = Audiencia.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "autoridad_id" in request.form:
        autoridad = Autoridad.query.get(request.form["autoridad_id"])
        if autoridad:
            consulta = consulta.filter_by(autoridad=autoridad)
    registros = consulta.order_by(Audiencia.creado.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for audiencia in registros:
        data.append(
            {
                "creado": audiencia.creado.strftime("%Y-%m-%d %H:%M:%S"),
                "autoridad": audiencia.autoridad.clave,
                "detalle": {
                    "tiempo": audiencia.tiempo,
                    "url": url_for("audiencias.detail", audiencia_id=audiencia.id),
                },
                "tipo_audiencia": audiencia.tipo_audiencia,
                "expediente": audiencia.expediente,
                "actores": audiencia.actores,
                "demandados": audiencia.demandados,
                "sala": audiencia.sala,
                "caracter": audiencia.caracter,
                "causa_penal": audiencia.causa_penal,
                "delitos": audiencia.delitos,
                "toca": audiencia.toca,
                "expediente_origen": audiencia.expediente_origen,
                "imputados": audiencia.imputados,
                "origen": audiencia.origen,
            }
        )
    # Entregar JSON
    return datatables.output(draw, total, data)


@audiencias.route("/audiencias/<int:audiencia_id>")
def detail(audiencia_id):
    """Detalle de una Audiencia"""
    audiencia = Audiencia.query.get_or_404(audiencia_id)
    return render_template("audiencias/detail.jinja2", audiencia=audiencia)


@audiencias.route("/audiencias/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva Audiencia"""
    autoridad = current_user.autoridad
    if autoridad.estatus != "A":
        flash("Su juzgado/autoridad no es activa.", "warning")
        return redirect(url_for("audiencias.list_active"))
    if autoridad.audiencia_categoria == "CIVIL FAMILIAR MERCANTIL LETRADO TCYA":
        return redirect(url_for("audiencias.new_generica"))
    if autoridad.audiencia_categoria == "MATERIA ACUSATORIO PENAL ORAL":
        return redirect(url_for("audiencias.new_mapo"))
    if autoridad.audiencia_categoria == "DISTRITALES":
        return redirect(url_for("audiencias.new_dipe"))
    if autoridad.audiencia_categoria == "SALAS":
        return redirect(url_for("audiencias.new_sape"))
    flash("El juzgado/autoridad no tiene una categoría de audiencias correcta.", "warning")
    return redirect(url_for("audiencias.list_active"))


@audiencias.route("/audiencias/nuevo/generica", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new_generica():
    """Nueva Audiencia Materias CIVIL FAMILIAR MERCANTIL LETRADO TCYA"""

    # Validar autoridad
    autoridad = current_user.autoridad
    if autoridad.estatus != "A":
        flash("El juzgado/autoridad no es activa.", "warning")
        return redirect(url_for("audiencias.list_active"))
    if autoridad.audiencia_categoria != "CIVIL FAMILIAR MERCANTIL LETRADO TCYA":
        flash("La categoría de audiencia no es CIVIL FAMILIAR MERCANTIL LETRADO TCYA.", "warning")
        return redirect(url_for("audiencias.list_active"))

    # Si viene el formulario
    form = AudienciaGenericaForm()
    if form.validate_on_submit():

        # Definir tiempo con la fecha y horas:minutos
        try:
            tiempo = combine_to_utc(form.tiempo_fecha.data, form.tiempo_horas_minutos.data)
            tiempo_mensaje = join_for_message(form.tiempo_fecha.data, form.tiempo_horas_minutos.data)
        except ValueError as error:
            flash(str(error), "warning")
            return render_template("audiencias/new_generica.jinja2", form=form)

        # Validar tipo de audiencia
        tipo_audiencia = safe_string(form.tipo_audiencia.data)
        if tipo_audiencia == "":
            tipo_audiencia = "NO DEFINIDO"

        # Validar expediente
        try:
            expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            return render_template("audiencias/new_generica.jinja2", form=form)

        # Insertar registro
        audiencia = Audiencia(
            autoridad=autoridad,
            tiempo=tiempo,
            tipo_audiencia=tipo_audiencia,
            expediente=expediente,
            actores=safe_string(form.actores.data),
            demandados=safe_string(form.demandados.data),
        )
        audiencia.save()

        # Mostrar mensaje de éxito e ir al detalle
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nueva audiencia en {autoridad.clave} para {tiempo_mensaje}"),
            url=url_for("audiencias.detail", audiencia_id=audiencia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)

    # Prellenado del formulario
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    return render_template("audiencias/new_generica.jinja2", form=form)


@audiencias.route("/audiencias/nuevo/mapo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new_mapo():
    """Nueva Audiencia MATERIA ACUSATORIO PENAL ORAL"""

    # Validar autoridad
    autoridad = current_user.autoridad
    if autoridad.estatus != "A":
        flash("El juzgado/autoridad no es activa.", "warning")
        return redirect(url_for("audiencias.list_active"))
    if autoridad.audiencia_categoria != "MATERIA ACUSATORIO PENAL ORAL":
        flash("La categoría de audiencia no es MATERIA ACUSATORIO PENAL ORAL.", "warning")
        return redirect(url_for("audiencias.list_active"))

    # Si viene el formulario
    form = AudienciaMapoForm()
    if form.validate_on_submit():

        # Definir tiempo con la fecha y horas:minutos
        try:
            tiempo = combine_to_utc(form.tiempo_fecha.data, form.tiempo_horas_minutos.data)
            tiempo_mensaje = join_for_message(form.tiempo_fecha.data, form.tiempo_horas_minutos.data)
        except ValueError as error:
            flash(str(error), "warning")
            return render_template("audiencias/new_mapo.jinja2", form=form)

        # Validar tipo de audiencia
        tipo_audiencia = safe_string(form.tipo_audiencia.data)
        if tipo_audiencia == "":
            tipo_audiencia = "NO DEFINIDO"

        # Insertar registro
        audiencia = Audiencia(
            autoridad=autoridad,
            tiempo=tiempo,
            tipo_audiencia=tipo_audiencia,
            sala=safe_string(form.sala.data),
            caracter=safe_string(form.caracter.data),
            causa_penal=safe_string(form.causa_penal.data),
            delitos=safe_string(form.delitos.data),
        )
        audiencia.save()

        # Mostrar mensaje de éxito e ir al detalle
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nueva audiencia en {autoridad.clave} para {tiempo_mensaje}"),
            url=url_for("audiencias.detail", audiencia_id=audiencia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)

    # Prellenado del formulario
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    return render_template("audiencias/new_mapo.jinja2", form=form)


@audiencias.route("/audiencias/nuevo/dipe", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new_dipe():
    """Nueva Audiencia DISTRITALES"""

    # Validar autoridad
    autoridad = current_user.autoridad
    if autoridad.estatus != "A":
        flash("El juzgado/autoridad no es activa.", "warning")
        return redirect(url_for("audiencias.list_active"))
    if autoridad.audiencia_categoria != "DISTRITALES":
        flash("La categoría de audiencia no es DISTRITALES.", "warning")
        return redirect(url_for("audiencias.list_active"))

    # Si viene el formulario
    form = AudienciaDipeForm()
    if form.validate_on_submit():

        # Definir tiempo con la fecha y horas:minutos
        try:
            tiempo = combine_to_utc(form.tiempo_fecha.data, form.tiempo_horas_minutos.data)
            tiempo_mensaje = join_for_message(form.tiempo_fecha.data, form.tiempo_horas_minutos.data)
        except ValueError as error:
            flash(str(error), "warning")
            return render_template("audiencias/new_dipe.jinja2", form=form)

        # Validar tipo de audiencia
        tipo_audiencia = safe_string(form.tipo_audiencia.data)
        if tipo_audiencia == "":
            tipo_audiencia = "NO DEFINIDO"

        # Validar expediente
        try:
            expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            return render_template("audiencias/new_dipe.jinja2", form=form)

        # Insertar registro
        audiencia = Audiencia(
            autoridad=autoridad,
            tiempo=tiempo,
            tipo_audiencia=tipo_audiencia,
            expediente=expediente,
            actores=safe_string(form.actores.data),
            demandados=safe_string(form.demandados.data),
            toca=safe_string(form.toca.data),
            expediente_origen=safe_string(form.expediente_origen.data),
            imputados=safe_string(form.imputados.data),
        )
        audiencia.save()

        # Mostrar mensaje de éxito e ir al detalle
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nueva audiencia en {autoridad.clave} para {tiempo_mensaje}"),
            url=url_for("audiencias.detail", audiencia_id=audiencia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)

    # Prellenado del formulario
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    return render_template("audiencias/new_dipe.jinja2", form=form)


@audiencias.route("/audiencias/nuevo/sape", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new_sape():
    """Nueva Audiencia SALAS"""

    # Validar autoridad
    autoridad = current_user.autoridad
    if autoridad.estatus != "A":
        flash("El juzgado/autoridad no es activa.", "warning")
        return redirect(url_for("audiencias.list_active"))
    if autoridad.audiencia_categoria != "SALAS":
        flash("La categoría de audiencia no es SALAS.", "warning")
        return redirect(url_for("audiencias.list_active"))

    # Si viene el formulario
    form = AudienciaSapeForm()
    if form.validate_on_submit():

        # Definir tiempo con la fecha y horas:minutos
        try:
            tiempo = combine_to_utc(form.tiempo_fecha.data, form.tiempo_horas_minutos.data)
            tiempo_mensaje = join_for_message(form.tiempo_fecha.data, form.tiempo_horas_minutos.data)
        except ValueError as error:
            flash(str(error), "warning")
            return render_template("audiencias/new_sape.jinja2", form=form)

        # Validar tipo de audiencia
        tipo_audiencia = safe_string(form.tipo_audiencia.data)
        if tipo_audiencia == "":
            tipo_audiencia = "NO DEFINIDO"

        # Validar expediente
        try:
            expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            return render_template("audiencias/new_sape.jinja2", form=form)

        # Insertar registro
        audiencia = Audiencia(
            autoridad=autoridad,
            tiempo=tiempo,
            tipo_audiencia=tipo_audiencia,
            expediente=expediente,
            actores=safe_string(form.actores.data),
            demandados=safe_string(form.demandados.data),
            toca=safe_string(form.toca.data),
            expediente_origen=safe_string(form.expediente_origen.data),
            delitos=safe_string(form.delitos.data),
            origen=safe_string(form.origen.data),
        )
        audiencia.save()

        # Mostrar mensaje de éxito e ir al detalle
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nueva audiencia en {autoridad.clave} para {tiempo_mensaje}"),
            url=url_for("audiencias.detail", audiencia_id=audiencia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)

    # Prellenado del formulario
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    return render_template("audiencias/new_sape.jinja2", form=form)


@audiencias.route("/audiencias/edicion/<int:audiencia_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(audiencia_id):
    """Editar Audiencia"""

    # Validad autoridad
    audiencia = Audiencia.query.get_or_404(audiencia_id)
    autoridad = audiencia.autoridad
    if autoridad.estatus != "A":
        flash("El juzgado/autoridad no es activa.", "warning")
        return redirect(url_for("audiencias.list_active"))

    # Redirigir
    if autoridad.audiencia_categoria == "CIVIL FAMILIAR MERCANTIL LETRADO TCYA":
        return redirect(url_for("audiencias.edit_generica", audiencia_id=audiencia_id))
    if autoridad.audiencia_categoria == "MATERIA ACUSATORIO PENAL ORAL":
        return redirect(url_for("audiencias.edit_mapo", audiencia_id=audiencia_id))
    if autoridad.audiencia_categoria == "DISTRITALES":
        return redirect(url_for("audiencias.edit_dipes", audiencia_id=audiencia_id))
    if autoridad.audiencia_categoria == "SALAS":
        return redirect(url_for("audiencias.edit_sape", audiencia_id=audiencia_id))

    # Mensaje por no reconocer la categoría de audiencias
    flash("El juzgado/autoridad no tiene una categoría de audiencias correcta.", "warning")
    return redirect(url_for("audiencias.list_active"))


@audiencias.route("/audiencias/edicion/generica/<int:audiencia_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit_generica(audiencia_id):
    """Editar Audiencia CIVIL FAMILIAR MERCANTIL LETRADO TCYA"""

    # Validar audiencia
    audiencia = Audiencia.query.get_or_404(audiencia_id)
    if not (current_user.can_admin("AUDIENCIAS") or current_user.autoridad_id == audiencia.autoridad_id):
        flash("No tiene permiso para editar esta audiencia.", "warning")
        return redirect(url_for("edictos.list_active"))

    # Validar autoridad
    autoridad = audiencia.autoridad
    if autoridad.estatus != "A":
        flash("El juzgado/autoridad no es activa.", "warning")
        return redirect(url_for("audiencias.list_active"))
    if autoridad.audiencia_categoria != "CIVIL FAMILIAR MERCANTIL LETRADO TCYA":
        flash("La categoría de audiencia no es CIVIL FAMILIAR MERCANTIL LETRADO TCYA.", "warning")
        return redirect(url_for("audiencias.list_active"))

    # Si viene el formulario
    form = AudienciaGenericaForm()
    if form.validate_on_submit():

        # Definir tiempo con la fecha y horas:minutos
        try:
            tiempo = combine_to_utc(form.tiempo_fecha.data, form.tiempo_horas_minutos.data)
            tiempo_mensaje = join_for_message(form.tiempo_fecha.data, form.tiempo_horas_minutos.data)
        except ValueError as error:
            flash(str(error), "warning")
            return render_template("audiencias/edit_generica.jinja2", form=form, audiencia=audiencia)

        # Validar tipo de audiencia
        tipo_audiencia = safe_string(form.tipo_audiencia.data)
        if tipo_audiencia == "":
            tipo_audiencia = "NO DEFINIDO"

        # Validar expediente
        try:
            expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            return render_template("audiencias/edit_generica.jinja2", form=form, audiencia=audiencia)

        # Actualizar registro
        audiencia.tiempo = tiempo
        audiencia.tipo_audiencia = tipo_audiencia
        audiencia.expediente = expediente
        audiencia.actores = safe_string(form.actores.data)
        audiencia.demandados = safe_string(form.demandados.data)
        audiencia.save()

        # Registrar en bitácora e ir al detalle
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editada la audiencia de {autoridad.clave} para {tiempo_mensaje}"),
            url=url_for("audiencias.detail", audiencia_id=audiencia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)

    # Descombinar el tiempo en fecha y horas:minutos
    form.tiempo_fecha.data, form.tiempo_horas_minutos.data = decombine_to_local(audiencia.tiempo)

    # Prellenado del formulario
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.tipo_audiencia.data = audiencia.tipo_audiencia
    form.expediente.data = audiencia.expediente
    form.actores.data = audiencia.actores
    form.demandados.data = audiencia.demandados
    return render_template("audiencias/edit_generica.jinja2", form=form, audiencia=audiencia)


@audiencias.route("/audiencias/edicion/mapo/<int:audiencia_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit_mapo(audiencia_id):
    """Editar Audiencia MATERIA ACUSATORIO PENAL ORAL"""

    # Validar audiencia
    audiencia = Audiencia.query.get_or_404(audiencia_id)
    if not (current_user.can_admin("AUDIENCIAS") or current_user.autoridad_id == audiencia.autoridad_id):
        flash("No tiene permiso para editar esta audiencia.", "warning")
        return redirect(url_for("edictos.list_active"))

    # Validar autoridad
    autoridad = audiencia.autoridad
    if autoridad.estatus != "A":
        flash("El juzgado/autoridad no es activa.", "warning")
        return redirect(url_for("audiencias.list_active"))
    if autoridad.audiencia_categoria != "MATERIA ACUSATORIO PENAL ORAL":
        flash("La categoría de audiencia no es MATERIA ACUSATORIO PENAL ORAL.", "warning")
        return redirect(url_for("audiencias.list_active"))

    # Si viene el formulario
    form = AudienciaMapoForm()
    if form.validate_on_submit():

        # Definir tiempo con la fecha y horas:minutos
        try:
            tiempo = combine_to_utc(form.tiempo_fecha.data, form.tiempo_horas_minutos.data)
            tiempo_mensaje = join_for_message(form.tiempo_fecha.data, form.tiempo_horas_minutos.data)
        except ValueError as error:
            flash(str(error), "warning")
            return render_template("audiencias/edit_mapo.jinja2", form=form, audiencia=audiencia)

        # Validar tipo de audiencia
        tipo_audiencia = safe_string(form.tipo_audiencia.data)
        if tipo_audiencia == "":
            tipo_audiencia = "NO DEFINIDO"

        # Actualizar registro
        audiencia.tiempo = tiempo
        audiencia.tipo_audiencia = tipo_audiencia
        audiencia.sala = safe_string(form.sala.data)
        audiencia.caracter = safe_string(form.caracter.data)
        audiencia.causa_penal = safe_string(form.causa_penal.data)
        audiencia.delitos = safe_string(form.delitos.data)
        audiencia.save()

        # Registrar en bitácora e ir al detalle
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editada la audiencia de {autoridad.clave} para {tiempo_mensaje}"),
            url=url_for("audiencias.detail", audiencia_id=audiencia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)

    # Descombinar el tiempo en fecha y horas:minutos
    form.tiempo_fecha.data, form.tiempo_horas_minutos.data = decombine_to_local(audiencia.tiempo)

    # Prellenado del formulario
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.tipo_audiencia.data = audiencia.tipo_audiencia
    form.sala.data = audiencia.sala
    form.caracter.data = audiencia.caracter
    form.causa_penal.data = audiencia.causa_penal
    form.delitos.data = audiencia.delitos
    return render_template("audiencias/edit_mapo.jinja2", form=form, audiencia=audiencia)


@audiencias.route("/audiencias/edicion/dipe/<int:audiencia_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit_dipe(audiencia_id):
    """Editar Audiencia DISTRITALES"""

    # Validar audiencia
    audiencia = Audiencia.query.get_or_404(audiencia_id)
    if not (current_user.can_admin("AUDIENCIAS") or current_user.autoridad_id == audiencia.autoridad_id):
        flash("No tiene permiso para editar esta audiencia.", "warning")
        return redirect(url_for("edictos.list_active"))

    # Validar autoridad
    autoridad = audiencia.autoridad
    if autoridad.estatus != "A":
        flash("El juzgado/autoridad no es activa.", "warning")
        return redirect(url_for("audiencias.list_active"))
    if autoridad.audiencia_categoria != "DISTRITALES":
        flash("La categoría de audiencia no es DISTRITALES.", "warning")
        return redirect(url_for("audiencias.list_active"))

    # Si viene el formulario
    form = AudienciaDipeForm()
    if form.validate_on_submit():

        # Definir tiempo con la fecha y horas:minutos
        try:
            tiempo = combine_to_utc(form.tiempo_fecha.data, form.tiempo_horas_minutos.data)
            tiempo_mensaje = join_for_message(form.tiempo_fecha.data, form.tiempo_horas_minutos.data)
        except ValueError as error:
            flash(str(error), "warning")
            return render_template("audiencias/edit_dipe.jinja2", form=form, audiencia=audiencia)

        # Validar tipo de audiencia
        tipo_audiencia = safe_string(form.tipo_audiencia.data)
        if tipo_audiencia == "":
            tipo_audiencia = "NO DEFINIDO"

        # Validar expediente
        try:
            expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            return render_template("audiencias/edit_dipe.jinja2", form=form, audiencia=audiencia)

        # Actualizar registro
        audiencia.tiempo = tiempo
        audiencia.tipo_audiencia = tipo_audiencia
        audiencia.expediente = expediente
        audiencia.actores = safe_string(form.actores.data)
        audiencia.demandados = safe_string(form.demandados.data)
        audiencia.toca = safe_string(form.toca.data)
        audiencia.expediente_origen = safe_string(form.expediente_origen.data)
        audiencia.imputados = safe_string(form.imputados.data)
        audiencia.save()

        # Registrar en bitácora e ir al detalle
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editada la audiencia de {autoridad.clave} para {tiempo_mensaje}"),
            url=url_for("audiencias.detail", audiencia_id=audiencia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)

    # Descombinar el tiempo en fecha y horas:minutos
    form.tiempo_fecha.data, form.tiempo_horas_minutos.data = decombine_to_local(audiencia.tiempo)

    # Prellenado del formulario
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.tipo_audiencia.data = audiencia.tipo_audiencia
    form.expediente.data = audiencia.expediente
    form.actores.data = audiencia.actores
    form.demandados.data = audiencia.demandados
    form.toca.data = audiencia.toca
    form.expediente_origen.data = audiencia.expediente_origen
    form.imputados.data = audiencia.imputados
    return render_template("audiencias/edit_dipe.jinja2", form=form, audiencia=audiencia)


@audiencias.route("/audiencias/edicion/sape/<int:audiencia_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit_sape(audiencia_id):
    """Editar Audiencia SALAS"""

    # Validar audiencia
    audiencia = Audiencia.query.get_or_404(audiencia_id)
    if not (current_user.can_admin("AUDIENCIAS") or current_user.autoridad_id == audiencia.autoridad_id):
        flash("No tiene permiso para editar esta audiencia.", "warning")
        return redirect(url_for("edictos.list_active"))

    # Validar autoridad
    autoridad = audiencia.autoridad
    if autoridad.estatus != "A":
        flash("El juzgado/autoridad no es activa.", "warning")
        return redirect(url_for("audiencias.list_active"))
    if autoridad.audiencia_categoria != "SALAS":
        flash("La categoría de audiencia no es SALAS.", "warning")
        return redirect(url_for("audiencias.list_active"))

    # Si viene el formulario
    form = AudienciaSapeForm()
    if form.validate_on_submit():

        # Definir tiempo con la fecha y horas:minutos
        try:
            tiempo = combine_to_utc(form.tiempo_fecha.data, form.tiempo_horas_minutos.data)
            tiempo_mensaje = join_for_message(form.tiempo_fecha.data, form.tiempo_horas_minutos.data)
        except ValueError as error:
            flash(str(error), "warning")
            return render_template("audiencias/edit_sape.jinja2", form=form, audiencia=audiencia)

        # Validar tipo de audiencia
        tipo_audiencia = safe_string(form.tipo_audiencia.data)
        if tipo_audiencia == "":
            tipo_audiencia = "NO DEFINIDO"

        # Validar expediente
        try:
            expediente = safe_expediente(form.expediente.data)
        except (IndexError, ValueError):
            flash("El expediente es incorrecto.", "warning")
            return render_template("audiencias/edit_sape.jinja2", form=form, audiencia=audiencia)

        # Actualizar registro
        audiencia.tiempo = tiempo
        audiencia.tipo_audiencia = tipo_audiencia
        audiencia.expediente = expediente
        audiencia.actores = safe_string(form.actores.data)
        audiencia.demandados = safe_string(form.demandados.data)
        audiencia.toca = safe_string(form.toca.data)
        audiencia.expediente_origen = safe_string(form.expediente_origen.data)
        audiencia.delitos = safe_string(form.delitos.data)
        audiencia.origen = safe_string(form.origen.data)
        audiencia.save()

        # Registrar en bitácora e ir al detalle
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editada la audiencia de {autoridad.clave} para {tiempo_mensaje}"),
            url=url_for("audiencias.detail", audiencia_id=audiencia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)

    # Descombinar el tiempo en fecha y horas:minutos
    form.tiempo_fecha.data, form.tiempo_horas_minutos.data = decombine_to_local(audiencia.tiempo)

    # Prellenado del formulario
    form.distrito.data = autoridad.distrito.nombre
    form.autoridad.data = autoridad.descripcion
    form.tipo_audiencia.data = audiencia.tipo_audiencia
    form.expediente.data = audiencia.expediente
    form.actores.data = audiencia.actores
    form.demandados.data = audiencia.demandados
    form.toca.data = audiencia.toca
    form.expediente_origen.data = audiencia.expediente_origen
    form.delitos.data = audiencia.delitos
    form.origen.data = audiencia.origen
    return render_template("audiencias/edit_sape.jinja2", form=form, audiencia=audiencia)


@audiencias.route("/audiencias/eliminar/<int:audiencia_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(audiencia_id):
    """Eliminar Audiencia"""
    audiencia = Audiencia.query.get_or_404(audiencia_id)
    if audiencia.estatus == "A":
        if current_user.can_admin("AUDIENCIAS") or current_user.autoridad_id == audiencia.autoridad_id:
            audiencia.delete()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message("Eliminada la audiencia"),
                url=url_for("audiencias.detail", audiencia_id=audiencia.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
        else:
            flash("No tiene permiso para eliminar.", "warning")
    return redirect(url_for("audiencias.detail", audiencia_id=audiencia.id))


@audiencias.route("/audiencias/recuperar/<int:audiencia_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(audiencia_id):
    """Recuperar Audiencia"""
    audiencia = Audiencia.query.get_or_404(audiencia_id)
    if audiencia.estatus == "B":
        if current_user.can_admin("AUDIENCIAS") or current_user.autoridad_id == audiencia.autoridad_id:
            audiencia.recover()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message("Recuperada la audiencia"),
                url=url_for("audiencias.detail", audiencia_id=audiencia.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
        else:
            flash("No tiene permiso para eliminar.", "warning")
    return redirect(url_for("audiencias.detail", audiencia_id=audiencia.id))

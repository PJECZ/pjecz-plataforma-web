"""
Autoridades, vistas
"""
import json
from datetime import date, datetime, timedelta

import pytz
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_clave, safe_string, safe_message

from sqlalchemy import or_

from plataforma_web.blueprints.audiencias.models import Audiencia
from plataforma_web.blueprints.autoridades.models import Autoridad
from plataforma_web.blueprints.autoridades.forms import AutoridadEditForm, AutoridadNewForm, AutoridadSearchForm
from plataforma_web.blueprints.bitacoras.models import Bitacora
from plataforma_web.blueprints.distritos.models import Distrito
from plataforma_web.blueprints.edictos.models import Edicto
from plataforma_web.blueprints.materias.models import Materia
from plataforma_web.blueprints.modulos.models import Modulo
from plataforma_web.blueprints.permisos.models import Permiso
from plataforma_web.blueprints.listas_de_acuerdos.models import ListaDeAcuerdo
from plataforma_web.blueprints.sentencias.models import Sentencia
from plataforma_web.blueprints.usuarios.decorators import permission_required

MODULO = "AUTORIDADES"

autoridades = Blueprint("autoridades", __name__, template_folder="templates")

HOY = date.today()
BREVE_LIMITE_DIAS = 15
BREVE_DESDE_DATETIME = datetime(year=HOY.year, month=HOY.month, day=HOY.day) + timedelta(days=-BREVE_LIMITE_DIAS)
ZONA_HORARIA = pytz.timezone("America/Mexico_City")

TARJETA_SATISFACTORIA = "bg-light"
TARJETA_ADVERTENCIA = "bg-warning"
TARJETA_VACIA = "bg-danger"
TARJETAS_LIMITE_REGISTROS = 5


@autoridades.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@autoridades.route("/autoridades/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Autoridades"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = Autoridad.query
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "distrito_id" in request.form:
        consulta = consulta.filter_by(distrito_id=request.form["distrito_id"])
    if "materia_id" in request.form:
        consulta = consulta.filter_by(materia_id=request.form["materia_id"])
    if "clave" in request.form:
        consulta = consulta.filter(Autoridad.clave.contains(safe_string(request.form["clave"])))
    if "descripcion" in request.form:
        consulta = consulta.filter(Autoridad.descripcion.contains(safe_string(request.form["descripcion"], to_uppercase=False)))
    if "organo_jurisdiccional" in request.form:
        consulta = consulta.filter(Autoridad.organo_jurisdiccional == safe_string(request.form["organo_jurisdiccional"]))
    if "caracteristicas" in request.form:
        if request.form["caracteristicas"] == "CEMASC":
            consulta = consulta.filter_by(es_cemasc=True)
        elif request.form["caracteristicas"] == "DEFENSORIA":
            consulta = consulta.filter_by(es_defensoria=True)
        elif request.form["caracteristicas"] == "JURISDICCIONAL":
            consulta = consulta.filter_by(es_jurisdiccional=True)
        elif request.form["caracteristicas"] == "NOTARIA":
            consulta = consulta.filter_by(es_notaria=True)
        elif request.form["caracteristicas"] == "ORGANO_ESPECIALIZADO":
            consulta = consulta.filter_by(es_organo_especializado=True)
        elif request.form["caracteristicas"] == "REVISOR_ESCRITURAS":
            consulta = consulta.filter_by(es_revisor_escrituras=True)
    registros = consulta.order_by(Autoridad.clave).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "clave": resultado.clave,
                    "url": url_for("autoridades.detail", autoridad_id=resultado.id),
                },
                "descripcion_corta": resultado.descripcion_corta,
                "organo_jurisdiccional": resultado.organo_jurisdiccional,
                "distrito": {
                    "nombre_corto": resultado.distrito.nombre_corto,
                    "url": url_for("distritos.detail", distrito_id=resultado.distrito_id) if current_user.can_view("DISTRITOS") else "",
                },
                "materia": {
                    "nombre": resultado.materia.nombre,
                    "url": url_for("materias.detail", materia_id=resultado.materia_id) if current_user.can_view("MATERIAS") else "",
                },
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@autoridades.route("/autoridades")
def list_active():
    """Listado de Autoridades activos"""
    return render_template(
        "autoridades/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Autoridades",
        estatus="A",
        distritos=Distrito.query.filter_by(es_distrito_judicial=True).filter_by(estatus="A").all(),
    )


@autoridades.route("/autoridades/inactivos")
@permission_required(MODULO, Permiso.MODIFICAR)
def list_inactive():
    """Listado de Autoridades inactivos"""
    return render_template(
        "autoridades/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Autoridades inactivos",
        estatus="B",
    )


@autoridades.route("/autoridades/buscar", methods=["GET", "POST"])
def search():
    """Buscar Autoridad"""
    form_search = AutoridadSearchForm()
    if form_search.validate_on_submit():
        busqueda = {"estatus": "A"}
        titulos = []
        if form_search.descripcion.data:
            descripcion = safe_string(form_search.descripcion.data, save_enie=True)
            if descripcion != "":
                busqueda["descripcion"] = descripcion
                titulos.append("descripción " + descripcion)
        if form_search.clave.data:
            clave = safe_string(form_search.clave.data)
            if clave != "":
                busqueda["clave"] = clave
                titulos.append("clave " + clave)
        return render_template(
            "autoridades/list.jinja2",
            filtros=json.dumps(busqueda),
            titulo="Autoridad con " + ", ".join(titulos),
            estatus="A",
        )
    return render_template("autoridades/search.jinja2", form=form_search)


@autoridades.route("/autoridades/<int:autoridad_id>")
def detail(autoridad_id):
    """Detalle de un Autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    return render_template("autoridades/detail.jinja2", autoridad=autoridad)


@autoridades.route("/autoridades/<int:autoridad_id>/audiencias_json", methods=["GET", "POST"])
def audiencias_json(autoridad_id):
    """Audiencias de una Autoridad en JSON"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    audiencias = Audiencia.query.filter(Audiencia.autoridad == autoridad).filter_by(estatus="A")
    # Listado
    listado = []
    desde = datetime.now()  # Desde este momento
    for audiencia in audiencias.filter(Audiencia.tiempo >= desde).order_by(Audiencia.tiempo).limit(TARJETAS_LIMITE_REGISTROS).all():
        listado.append(
            {
                "tiempo": audiencia.tiempo.strftime("%Y-%m-%d %H:%M"),
                "tipo_audiencia": audiencia.tipo_audiencia,
                "url": url_for("audiencias.detail", audiencia_id=audiencia.id),
            }
        )
    # Breve
    estilo = TARJETA_SATISFACTORIA
    total = audiencias.count()
    if total > 0:
        breve = f"Total {total}. "
        if len(listado) > 0:
            breve += "Desde " + desde.strftime("%Y-%m-%d %H:%M") + ". "
        else:
            breve += "No hay eventos en la agenda de hoy."
            estilo = TARJETA_ADVERTENCIA
    else:
        breve = "Nunca ha agendado Audiencias. "
        estilo = TARJETA_VACIA
    # Entregar JSON
    return {
        "titulo": "Agenda de Audiencias",
        "breve": breve,
        "listado": listado,
        "url": url_for("audiencias.list_autoridad_audiencias", autoridad_id=autoridad_id),
        "style": estilo,
    }


@autoridades.route("/autoridades/<int:autoridad_id>/edictos_json", methods=["GET", "POST"])
def edictos_json(autoridad_id):
    """Edictos de una Autoridad en JSON"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    edictos = Edicto.query.filter(Edicto.autoridad == autoridad).filter_by(estatus="A")
    # Listado
    listado = []
    for edicto in edictos.order_by(Edicto.creado.desc()).limit(TARJETAS_LIMITE_REGISTROS).all():
        listado.append(
            {
                "expediente": edicto.expediente,
                "descripcion": edicto.descripcion,
                "url": url_for("edictos.detail", edicto_id=edicto.id),
            }
        )
    # Breve
    estilo = TARJETA_SATISFACTORIA
    total = edictos.count()
    if total > 0:
        breve = f"Total {total}. "
        cantidad = edictos.filter(Edicto.creado >= BREVE_DESDE_DATETIME).count()
        if cantidad > 0:
            breve += f"Se subieron {cantidad} en {BREVE_LIMITE_DIAS} días."
        else:
            breve += f"Ninguno en {BREVE_LIMITE_DIAS} días."
            estilo = TARJETA_ADVERTENCIA
    else:
        breve = "Nunca a subido Edictos."
        estilo = TARJETA_VACIA
    # Entregar JSON
    return {
        "titulo": "Edictos",
        "breve": breve,
        "listado": listado,
        "url": url_for("edictos.list_autoridad_edictos", autoridad_id=autoridad_id),
        "style": estilo,
    }


@autoridades.route("/autoridades/<int:autoridad_id>/listas_de_acuerdos_json", methods=["GET", "POST"])
def listas_de_acuerdos_json(autoridad_id):
    """Listas de Acuerdos de una Autoridad en JSON"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    listas_de_acuerdos = ListaDeAcuerdo.query.filter(ListaDeAcuerdo.autoridad == autoridad).filter_by(estatus="A")
    # Listado
    listado = []
    for lista_de_acuerdo in listas_de_acuerdos.order_by(ListaDeAcuerdo.creado.desc()).limit(TARJETAS_LIMITE_REGISTROS).all():
        listado.append(
            {
                "fecha": lista_de_acuerdo.fecha.strftime("%Y-%m-%d"),
                "url": url_for("listas_de_acuerdos.detail", lista_de_acuerdo_id=lista_de_acuerdo.id),
            }
        )
    # Breve
    estilo = TARJETA_SATISFACTORIA
    total = listas_de_acuerdos.count()
    if total > 0:
        breve = f"Total {total}. "
    else:
        breve = "Nunca a subido Listas de Acuerdos."
        estilo = TARJETA_VACIA
    # Entregar JSON
    return {
        "titulo": "Listas de Acuerdos",
        "breve": breve,
        "listado": listado,
        "url": url_for("listas_de_acuerdos.list_autoridad_listas_de_acuerdos", autoridad_id=autoridad_id),
        "style": estilo,
    }


@autoridades.route("/autoridades/<int:autoridad_id>/sentencias_json", methods=["GET", "POST"])
def sentencias_json(autoridad_id):
    """Sentencias de una Autoridad en JSON"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    sentencias = Sentencia.query.filter(Sentencia.autoridad == autoridad).filter_by(estatus="A")
    # Listado
    listado = []
    for sentencia in sentencias.order_by(Sentencia.creado.desc()).limit(TARJETAS_LIMITE_REGISTROS).all():
        listado.append(
            {
                "sentencia": sentencia.sentencia,
                "materia_tipo_juicio": sentencia.materia_tipo_juicio.descripcion,
                "url": url_for("sentencias.detail", sentencia_id=sentencia.id),
            }
        )
    # Breve
    estilo = TARJETA_SATISFACTORIA
    total = sentencias.count()
    if total > 0:
        breve = f"Total {total}. "
        cantidad = sentencias.filter(Sentencia.creado >= BREVE_DESDE_DATETIME).count()
        if cantidad > 0:
            breve += f"Se subieron {cantidad} en {BREVE_LIMITE_DIAS} días."
        else:
            breve += f"Ninguno en {BREVE_LIMITE_DIAS} días."
            estilo = TARJETA_ADVERTENCIA
    else:
        breve = "Nunca a subido V.P. de Sentencias."
        estilo = TARJETA_VACIA
    # Entregar JSON
    return {
        "titulo": "V.P. de Sentencias",
        "breve": breve,
        "listado": listado,
        "url": url_for("sentencias.list_autoridad_sentencias", autoridad_id=autoridad_id),
        "style": estilo,
    }


@autoridades.route("/autoridades/nuevo", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva Autoridad"""
    form = AutoridadNewForm()
    if form.validate_on_submit():
        # Validar que la clave no se repita
        clave = safe_string(form.clave.data)
        if Autoridad.query.filter_by(clave=clave).first():
            flash("La clave ya está en uso. Debe de ser única.", "warning")
        else:
            distrito = form.distrito.data
            descripcion = safe_string(form.descripcion.data, save_enie=True)
            es_jurisdiccional = form.es_jurisdiccional.data
            es_notaria = form.es_notaria.data
            es_revisor_escrituras = form.es_revisor_escrituras.data
            directorio = f"{distrito.nombre}/{descripcion}"
            directorio_listas_de_acuerdos = ""
            directorio_sentencias = ""
            directorio_edictos = ""
            directorio_glosas = ""
            limite_dias_listas_de_acuerdos = 0
            if es_jurisdiccional:
                directorio_edictos = directorio
                directorio_listas_de_acuerdos = directorio
                directorio_sentencias = directorio
                directorio_glosas = directorio
                limite_dias_listas_de_acuerdos = 1
            if es_notaria:
                directorio_edictos = directorio
            autoridad = Autoridad(
                distrito=distrito,
                descripcion=descripcion,
                descripcion_corta=safe_string(form.descripcion_corta.data, save_enie=True),
                clave=clave,
                es_archivo_solicitante=form.es_archivo_solicitante.data,
                es_cemasc=form.es_cemasc.data,
                es_defensoria=form.es_defensoria.data,
                es_jurisdiccional=es_jurisdiccional,
                es_notaria=es_notaria,
                es_organo_especializado=form.es_organo_especializado.data,
                es_revisor_escrituras=es_revisor_escrituras,
                organo_jurisdiccional=form.organo_jurisdiccional.data,
                materia=form.materia.data,
                audiencia_categoria=form.audiencia_categoria.data,
                directorio_listas_de_acuerdos=directorio_listas_de_acuerdos,
                directorio_sentencias=directorio_sentencias,
                directorio_edictos=directorio_edictos,
                directorio_glosas=directorio_glosas,
                limite_dias_listas_de_acuerdos=limite_dias_listas_de_acuerdos,
            )
            autoridad.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Nueva autoridad {autoridad.clave}"),
                url=url_for("autoridades.detail", autoridad_id=autoridad.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.materia.data = Materia.query.get(1)  # Materia NO DEFINIDO
    return render_template("autoridades/new.jinja2", form=form)


@autoridades.route("/autoridades/edicion/<int:autoridad_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(autoridad_id):
    """Editar Autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    form = AutoridadEditForm()
    if form.validate_on_submit():
        es_valido = True
        # Si cambia la clave verificar que no este en uso
        clave = safe_clave(form.clave.data)
        if autoridad.clave != clave:
            oficina_existente = Autoridad.query.filter_by(clave=clave).first()
            if oficina_existente and oficina_existente.id != autoridad_id:
                es_valido = False
                flash("La clave ya está en uso. Debe de ser única.", "warning")
        # Si es valido actualizar
        if es_valido:
            autoridad.distrito = form.distrito.data
            autoridad.descripcion = safe_string(form.descripcion.data, save_enie=True)
            autoridad.descripcion_corta = safe_string(form.descripcion_corta.data, save_enie=True)
            autoridad.clave = clave
            autoridad.es_archivo_solicitante = form.es_archivo_solicitante.data
            autoridad.es_cemasc = form.es_cemasc.data
            autoridad.es_defensoria = form.es_defensoria.data
            autoridad.es_jurisdiccional = form.es_jurisdiccional.data
            autoridad.es_notaria = form.es_notaria.data
            autoridad.es_organo_especializado = form.es_organo_especializado.data
            autoridad.es_revisor_escrituras = form.es_revisor_escrituras.data
            autoridad.organo_jurisdiccional = form.organo_jurisdiccional.data
            autoridad.materia = form.materia.data
            autoridad.audiencia_categoria = form.audiencia_categoria.data
            autoridad.directorio_listas_de_acuerdos = form.directorio_listas_de_acuerdos.data.strip()
            autoridad.directorio_sentencias = form.directorio_sentencias.data.strip()
            autoridad.directorio_edictos = form.directorio_edictos.data.strip()
            autoridad.directorio_glosas = form.directorio_glosas.data.strip()
            autoridad.limite_dias_listas_de_acuerdos = form.limite_dias_listas_de_acuerdos.data
            autoridad.datawarehouse_id = form.datawarehouse_id.data
            autoridad.save()
            bitacora = Bitacora(
                modulo=Modulo.query.filter_by(nombre=MODULO).first(),
                usuario=current_user,
                descripcion=safe_message(f"Editada autoridad {autoridad.clave}"),
                url=url_for("autoridades.detail", autoridad_id=autoridad.id),
            )
            bitacora.save()
            flash(bitacora.descripcion, "success")
            return redirect(bitacora.url)
    form.distrito.data = autoridad.distrito
    form.descripcion.data = autoridad.descripcion
    form.descripcion_corta.data = autoridad.descripcion_corta
    form.clave.data = autoridad.clave
    form.es_archivo_solicitante.data = autoridad.es_archivo_solicitante
    form.es_cemasc.data = autoridad.es_cemasc
    form.es_defensoria.data = autoridad.es_defensoria
    form.es_jurisdiccional.data = autoridad.es_jurisdiccional
    form.es_notaria.data = autoridad.es_notaria
    form.es_organo_especializado.data = autoridad.es_organo_especializado
    form.es_revisor_escrituras.data = autoridad.es_revisor_escrituras
    form.organo_jurisdiccional.data = autoridad.organo_jurisdiccional
    form.materia.data = autoridad.materia
    form.audiencia_categoria.data = autoridad.audiencia_categoria
    form.directorio_listas_de_acuerdos.data = autoridad.directorio_listas_de_acuerdos
    form.directorio_sentencias.data = autoridad.directorio_sentencias
    form.directorio_edictos.data = autoridad.directorio_edictos
    form.directorio_glosas.data = autoridad.directorio_glosas
    form.limite_dias_listas_de_acuerdos.data = autoridad.limite_dias_listas_de_acuerdos
    form.datawarehouse_id.data = autoridad.datawarehouse_id
    return render_template("autoridades/edit.jinja2", form=form, autoridad=autoridad)


@autoridades.route("/autoridades/eliminar/<int:autoridad_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def delete(autoridad_id):
    """Eliminar Autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if autoridad.estatus == "A":
        autoridad.delete()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminada autoridad {autoridad.clave}"),
            url=url_for("autoridades.detail", autoridad_id=autoridad.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))


@autoridades.route("/autoridades/recuperar/<int:autoridad_id>")
@permission_required(MODULO, Permiso.MODIFICAR)
def recover(autoridad_id):
    """Recuperar Autoridad"""
    autoridad = Autoridad.query.get_or_404(autoridad_id)
    if autoridad.estatus == "B":
        autoridad.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperada autoridad {autoridad.clave}"),
            url=url_for("autoridades.detail", autoridad_id=autoridad.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    return redirect(url_for("autoridades.detail", autoridad_id=autoridad.id))


@autoridades.route("/autoridades/notarias_json", methods=["POST"])
def query_notarias_json():
    """Proporcionar el JSON de autoridades para elegir Notarías con un Select2"""
    consulta = Autoridad.query.filter(Autoridad.estatus == "A").filter_by(es_notaria=True, es_jurisdiccional=True)
    if "searchString" in request.form:
        consulta = consulta.filter(Autoridad.descripcion.contains(request.form["searchString"]))
    results = []
    for autoridad in consulta.order_by(Autoridad.id).limit(15).all():
        results.append({"id": autoridad.id, "text": autoridad.distrito.nombre_corto + "  :  " + autoridad.descripcion, "nombre": autoridad.distrito.nombre + " : " + autoridad.descripcion})
    return {"results": results, "pagination": {"more": False}}


@autoridades.route("/autoridades/juzgados_json", methods=["POST"])
def query_juzgados_json():
    """Proporcionar el JSON de autoridades para elegir Juzgados con un Select2"""
    consulta = Autoridad.query.filter(Autoridad.estatus == "A")
    if "es_jurisdiccional" in request.form:
        # Verificar si esta seleccionado es_jurisdiccional
        consulta = consulta.filter_by(es_jurisdiccional=True)
        # Consultar si el organo jurisdiccional es el correcto
        consulta = consulta.filter(Autoridad.organo_jurisdiccional.between("JUZGADO DE PRIMERA INSTANCIA", "JUZGADO DE PRIMERA INSTANCIA ORAL"))
    if "clave" in request.form:
        texto = safe_string(request.form["clave"]).upper()
        consulta = consulta.filter(Autoridad.clave.contains(texto))
    results = []
    for autoridad in consulta.order_by(Autoridad.id).limit(15).all():
        results.append({"id": autoridad.id, "text": autoridad.clave + "  : " + autoridad.descripcion_corta})
    return {"results": results, "pagination": {"more": False}}


@autoridades.route("/autoridades/es_revisor_escrituras_json", methods=["POST"])
def query_es_revisor_escrituras_json():
    """Proporcionar el JSON de autoridades para elegir un juzgado si esta seleccionado la opción es_revisor_escrituras con un Select2"""
    consulta = Autoridad.query.filter(Autoridad.estatus == "A").filter_by(es_revisor_escrituras=True)
    if "searchString" in request.form:
        consulta = consulta.filter(Autoridad.descripcion.contains(request.form["searchString"]))
    results = []
    for autoridad in consulta.order_by(Autoridad.id).limit(15).all():
        results.append({"id": autoridad.id, "text": autoridad.distrito.nombre_corto + "  :  " + autoridad.descripcion, "nombre": autoridad.distrito.nombre + " : " + autoridad.descripcion})
    return {"results": results, "pagination": {"more": False}}

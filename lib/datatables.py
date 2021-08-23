"""
Datatables
"""
from flask import request


def get_parameters():
    """Tomar parametros"""
    try:
        draw = int(request.form["draw"])
        start = int(request.form["start"])
        rows_per_page = int(request.form["length"])
    except (TypeError, ValueError):
        draw = 1
        start = 1
        rows_per_page = 10
    return draw, start, rows_per_page


def output(draw, total, data):
    """Entregar JSON"""
    return {
        "draw": draw,
        "iTotalRecords": total,
        "iTotalDisplayRecords": total,
        "aaData": data,
    }

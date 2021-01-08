"""
Siguiente URL segura
"""
from urllib.parse import urljoin
from flask import request


def safe_next_url(target):
    """ Siguiente URL segura """
    return urljoin(request.host_url, target)

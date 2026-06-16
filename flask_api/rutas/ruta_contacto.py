# flask_api/rutas/ruta_contacto.py
from flask import Blueprint
from flask_api.controlador.control_contacto import procesar_contacto

contacto_bp = Blueprint("contacto", __name__, url_prefix="/contacto")

@contacto_bp.route("", methods=["POST"]) 
def contacto():
    return procesar_contacto()

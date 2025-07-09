from flask import Blueprint, request
from flask_api.controlador.control_registro import register_user

registro_bp = Blueprint('registro', __name__, url_prefix='/auth')

@registro_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    return register_user(data)

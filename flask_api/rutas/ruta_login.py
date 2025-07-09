from flask import Blueprint, request
from flask_api.controlador.control_login import login_user

login_bp = Blueprint('login', __name__, url_prefix='/auth')

@login_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    return login_user(data)

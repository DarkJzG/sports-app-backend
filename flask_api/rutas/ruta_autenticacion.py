# flask_api/rutas/ruta_autenticacion.py
from flask import Blueprint, request
from flask_api.controlador.control_autenticacion import (
    login_user,
    register_user,
    verificar_cuenta,
    solicitar_reset_password,
    confirmar_reset_password,
    reenviar_verificacion
)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# -------------------------------
# Registro e inicio de sesión
# -------------------------------
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    return register_user(data)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    return login_user(data)

# -------------------------------
# Verificación de correo
# -------------------------------
@auth_bp.route("/verificar/<token>", methods=["GET"])
def verificar(token):
    return verificar_cuenta(token)

# -------------------------------
# Recuperación de contraseña
# -------------------------------
@auth_bp.route("/reset-request", methods=["POST"])
def reset_request():
    data = request.get_json()
    return solicitar_reset_password(data)

@auth_bp.route("/reset-confirm", methods=["POST"])
def reset_confirm():
    data = request.get_json()
    return confirmar_reset_password(data)


# -------------------------------
# Reenviar verificación
# -------------------------------
@auth_bp.route("/resend-verification", methods=["POST"])
def resend_verification():
    data = request.get_json()
    return reenviar_verificacion(data)
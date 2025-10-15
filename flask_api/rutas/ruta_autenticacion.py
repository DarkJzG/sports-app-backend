from flask import Blueprint, request
from flask_api.controlador.control_autenticacion import (
    register_user,
    login_user,
    verificar_cuenta,
    reenviar_verificacion,
    solicitar_reset_password,
    confirmar_reset_password,
    cambiar_password,
)
from flask_jwt_extended import jwt_required


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Registro
@auth_bp.route("/register", methods=["POST"])
def register():
    return register_user(request.get_json())

# Login
@auth_bp.route("/login", methods=["POST"])
def login():
    return login_user(request.get_json())

# Verificar correo
@auth_bp.route("/verificar", methods=["GET"])
def verificar():
    token = request.args.get("token")
    return verificar_cuenta(token)

# Reenviar verificación
@auth_bp.route("/resend-verification", methods=["POST"])
def resend_verification():
    return reenviar_verificacion(request.get_json())

# Recuperar contraseña
@auth_bp.route("/reset-request", methods=["POST"])
def reset_request():
    return solicitar_reset_password(request.get_json())

# Confirmar reset
@auth_bp.route("/reset-confirm", methods=["POST"])
def reset_confirm():
    return confirmar_reset_password(request.get_json())

# Cambiar contraseña (autenticado)
@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    return cambiar_password(request.get_json())


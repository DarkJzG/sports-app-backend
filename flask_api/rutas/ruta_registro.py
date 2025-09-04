import secrets
from flask import Blueprint, request, jsonify, redirect
from flask_api.controlador.control_registro import register_user
from flask_api.modelo.modelo_usuario import get_users_collection
from flask_api.funciones.enviar_correo import enviar_correo_verificacion
from flask_api.funciones.enviar_correo import enviar_correo_reset
from werkzeug.security import generate_password_hash


registro_bp = Blueprint('registro', __name__, url_prefix='/auth')

@registro_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    return register_user(data)

@registro_bp.route("/verificar", methods=["GET"])
def verificar_correo():
    token = request.args.get('token')
    if not token:
        return jsonify({'ok': False, 'msg': 'Token faltante'}), 400

    users = get_users_collection()
    user = users.find_one({'token_verificacion': token})

    if not user:
        return jsonify({'ok': False, 'msg': 'Token inválido o expirado'}), 400

    users.update_one(
        {'_id': user['_id']},
        {'$set': {'verificado': True}, '$unset': {'token_verificacion': ""}}
    )

    # Puedes redirigir al login del frontend si quieres
    return redirect("http://192.168.3.175:3000/login?verificado=true")


@registro_bp.route("/olvidar-password", methods=["POST"])
def forgot_password():
    correo = request.json.get("correo")
    users = get_users_collection()
    user = users.find_one({'correo': correo})
    if not user:
        return jsonify({'ok': False, 'msg': 'Correo no registrado'}), 404

    token_reset = secrets.token_urlsafe(32)
    users.update_one({'_id': user['_id']}, {'$set': {'token_reset': token_reset}})
    
    # enviar correo con link
    from flask_api.funciones.enviar_correo import enviar_correo_reset
    enviar_correo_reset(correo, user['nombre'], token_reset)

    return jsonify({'ok': True, 'msg': 'Correo de recuperación enviado'})


@registro_bp.route("/restablecer-password", methods=["POST"])
def reset_password():
    token = request.json.get("token")
    nueva_password = request.json.get("password")
    
    if not token or not nueva_password:
        return jsonify({'ok': False, 'msg': 'Datos incompletos'}), 400

    users = get_users_collection()
    user = users.find_one({'token_reset': token})
    if not user:
        return jsonify({'ok': False, 'msg': 'Token inválido'}), 400

    hashed_pw = generate_password_hash(nueva_password)
    users.update_one({'_id': user['_id']}, {
        '$set': {'password': hashed_pw},
        '$unset': {'token_reset': ""}
    })

    return jsonify({'ok': True, 'msg': 'Contraseña actualizada correctamente'})

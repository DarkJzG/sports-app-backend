from werkzeug.security import generate_password_hash
from flask_api.modelo.modelo_usuario import get_users_collection
from flask import jsonify
from flask_api.funciones.enviar_correo import enviar_correo_verificacion
import secrets

def register_user(data):
    nombre = data.get('nombre')
    correo = data.get('correo')
    password = data.get('password')

    if not nombre or not correo or not password:
        return jsonify({'ok': False, 'msg': 'Datos incompletos'}), 400

    users = get_users_collection()
    if users.find_one({'correo': correo}):
        return jsonify({'ok': False, 'msg': 'El correo ya está registrado'}), 400

    hashed_pw = generate_password_hash(password)
    token_verificacion = secrets.token_urlsafe(32)

    user = {
        'nombre': nombre,
        'apellido': "",
        'rol': "cliente",
        'correo': correo,
        'password': hashed_pw,
        'ciudad': "",
        'codigo_postal': "",
        'direccion_principal': "",
        'direccion_secundaria': "",
        'pais': "",
        'telefono': "",
        'verificado': False,
        'token_verificacion': token_verificacion
    }
    users.insert_one(user)

    # Enviar correo de verificación
    try:
        enviar_correo_verificacion(correo, nombre, token_verificacion)
    except Exception as e:
        print("Error al enviar correo:", e)

    return jsonify({'ok': True, 'msg': 'Usuario registrado. Por favor verifica tu correo.'}), 201

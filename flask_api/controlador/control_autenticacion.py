import secrets
from datetime import timedelta
from flask import jsonify, current_app
from flask_jwt_extended import create_access_token, decode_token
from werkzeug.security import generate_password_hash, check_password_hash
from flask_api.modelo.modelo_usuario import get_users_collection
from flask_api.funciones.enviar_correo import (
    enviar_correo_verificacion,
    enviar_correo_reset,
)

# -------------------------------
# Registro de usuario
# -------------------------------
def register_user(data):
    nombre = data.get("nombre")
    correo = data.get("correo")
    password = data.get("password")

    if not nombre or not correo or not password:
        return jsonify({"ok": False, "msg": "Datos incompletos"}), 400

    users = get_users_collection()
    if users.find_one({"correo": correo}):
        return jsonify({"ok": False, "msg": "El correo ya está registrado"}), 400

    hashed_pw = generate_password_hash(password)

    # Generar token de verificación (JWT con expiración)
    token_verificacion = create_access_token(
        identity=correo, expires_delta=timedelta(hours=24)
    )

    user = {
        "nombre": nombre,
        "apellido": "",
        "rol": "cliente",
        "correo": correo,
        "password": hashed_pw,
        "ciudad": "",
        "codigo_postal": "",
        "direccion_principal": "",
        "direccion_secundaria": "",
        "pais": "",
        "telefono": "",
        "verificado": False,
        "token_verificacion": token_verificacion,
    }
    users.insert_one(user)

    # Enviar correo de verificación
    try:
        enviar_correo_verificacion(correo, nombre, token_verificacion)
    except Exception as e:
        print("❌ Error al enviar correo:", e)

    return jsonify({"ok": True, "msg": "Usuario registrado. Verifica tu correo."}), 201


# -------------------------------
# Login
# -------------------------------
def login_user(data):
    correo = data.get("correo")
    password = data.get("password")
    if not correo or not password:
        return jsonify({"ok": False, "msg": "Datos incompletos"}), 400

    users = get_users_collection()
    user = users.find_one({"correo": correo})

    if not user:
        return jsonify({"ok": False, "msg": "Usuario no encontrado"}), 404

    if not check_password_hash(user["password"], password):
        return jsonify({"ok": False, "msg": "Correo o contraseña incorrectos"}), 401

    if not user.get("verificado", False):
        return jsonify({"ok": False, "msg": "Cuenta no verificada"}), 403

    # Generar access token para sesión (ejemplo: 7 días)
    access_token = create_access_token(
        identity=str(user["_id"]), expires_delta=timedelta(days=7)
    )

    return jsonify(
        {
            "ok": True,
            "msg": "Inicio de sesión exitoso",
            "token": access_token,
            "usuario": {
                "id": str(user["_id"]),
                "nombre": user["nombre"],
                "correo": user["correo"],
                "rol": user.get("rol", "cliente"),
            },
        }
    )


# -------------------------------
# Verificación de cuenta
# -------------------------------
def verificar_cuenta(token):
    try:
        decoded = decode_token(token)
        correo = decoded["sub"]  # identidad = correo
    except Exception as e:
        return jsonify({"ok": False, "msg": "Token inválido o expirado"}), 400

    users = get_users_collection()
    user = users.find_one({"correo": correo})

    if not user:
        return jsonify({"ok": False, "msg": "Usuario no encontrado"}), 404

    if user.get("verificado", False):
        return jsonify({"ok": True, "msg": "La cuenta ya estaba verificada"}), 200

    users.update_one({"_id": user["_id"]}, {"$set": {"verificado": True}})
    return jsonify({"ok": True, "msg": "Cuenta verificada correctamente"}), 200


# -------------------------------
# Solicitud de reset password
# -------------------------------
def solicitar_reset_password(data):
    correo = data.get("correo")
    if not correo:
        return jsonify({"ok": False, "msg": "Correo requerido"}), 400

    users = get_users_collection()
    user = users.find_one({"correo": correo})

    if not user:
        return jsonify({"ok": False, "msg": "Usuario no encontrado"}), 404

    # Token válido por 15 minutos
    token_reset = create_access_token(identity=correo, expires_delta=timedelta(minutes=15))

    try:
        enviar_correo_reset(correo, user["nombre"], token_reset)
    except Exception as e:
        print("❌ Error al enviar correo reset:", e)

    return jsonify({"ok": True, "msg": "Correo de recuperación enviado"}), 200


# -------------------------------
# Confirmar reset password
# -------------------------------
def confirmar_reset_password(data):
    token = data.get("token")
    new_password = data.get("password")

    if not token or not new_password:
        return jsonify({"ok": False, "msg": "Datos incompletos"}), 400

    try:
        decoded = decode_token(token)
        correo = decoded["sub"]
    except Exception:
        return jsonify({"ok": False, "msg": "Token inválido o expirado"}), 400

    users = get_users_collection()
    user = users.find_one({"correo": correo})

    if not user:
        return jsonify({"ok": False, "msg": "Usuario no encontrado"}), 404

    hashed_pw = generate_password_hash(new_password)
    users.update_one({"_id": user["_id"]}, {"$set": {"password": hashed_pw}})

    return jsonify({"ok": True, "msg": "Contraseña actualizada correctamente"}), 200


# -------------------------------
# Reenviar verificación de cuenta
# -------------------------------
from datetime import timedelta
from flask_jwt_extended import create_access_token

def reenviar_verificacion(data):
    correo = data.get("correo")
    if not correo:
        return jsonify({"ok": False, "msg": "Correo requerido"}), 400

    users = get_users_collection()
    user = users.find_one({"correo": correo})

    if not user:
        return jsonify({"ok": False, "msg": "Usuario no encontrado"}), 404

    if user.get("verificado", False):
        return jsonify({"ok": True, "msg": "La cuenta ya está verificada"}), 200

    # Nuevo token válido 24h
    token_verificacion = create_access_token(identity=correo, expires_delta=timedelta(hours=24))
    users.update_one({"_id": user["_id"]}, {"$set": {"token_verificacion": token_verificacion}})

    try:
        enviar_correo_verificacion(user["correo"], user["nombre"], token_verificacion)
    except Exception as e:
        print("❌ Error al enviar correo de verificación:", e)

    return jsonify({"ok": True, "msg": "Se envió un nuevo enlace de verificación"}), 200

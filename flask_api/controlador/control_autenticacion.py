import secrets
import re
from datetime import timedelta
from flask import jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    decode_token,
    get_jwt_identity,
    jwt_required,
)
from bson import ObjectId

from flask_api.modelo.modelo_usuario import get_users_collection
from flask_api.funciones.enviar_correo import (
    enviar_correo_verificacion,
    enviar_correo_reset,
)


# REGISTRO DE USUARIO
def register_user(data):
    nombre = data.get("nombre")
    correo = data.get("correo")
    password = data.get("password")

    if not nombre or not correo or not password:
        return jsonify({"ok": False, "msg": "Datos incompletos"}), 400

    users = get_users_collection()
    if users.find_one({"correo": correo}):
        return jsonify({"ok": False, "msg": "El correo ya está registrado"}), 400

    # Validar seguridad de contraseña
    if (
        len(password) < 8
        or not re.search(r"[A-Z]", password)
        or not re.search(r"\d", password)
        or not re.search(r"[!@#$%^&*]", password)
    ):
        return jsonify({
            "ok": False,
            "msg": "La contraseña debe tener al menos 8 caracteres, una mayúscula, un número y un símbolo especial."
        }), 400

    hashed_pw = generate_password_hash(password)
    token_verificacion = create_access_token(
        identity=correo, expires_delta=timedelta(hours=24)
    )

    user = {
        "nombre": nombre,
        "apellido": "",
        "rol": "cliente",
        "correo": correo,
        "password": hashed_pw,
        "verificado": False,
        "token_verificacion": token_verificacion,
    }

    users.insert_one(user)

    # Enviar correo de verificación
    try:
        enviar_correo_verificacion(correo, nombre, token_verificacion)
    except Exception as e:
        print("❌ Error al enviar correo de verificación:", e)

    return jsonify({"ok": True, "msg": "Usuario registrado. Verifica tu correo."}), 201


# LOGIN CON JWT
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

    # Generar token JWT válido por 7 días
    access_token = create_access_token(
        identity=str(user["_id"]), expires_delta=timedelta(days=7)
    )

    return jsonify({
        "ok": True,
        "msg": "Inicio de sesión exitoso",
        "token": access_token,
        "usuario": {
            "id": str(user["_id"]),
            "nombre": user["nombre"],
            "correo": user["correo"],
            "rol": user.get("rol", "cliente"),
        },
    }), 200


# VERIFICACIÓN DE CUENTA
def verificar_cuenta(token):
    if not token or token == "null":
        return jsonify({"ok": False, "msg": "Token de verificación faltante o inválido"}), 400

    try:
        decoded = decode_token(token)
        correo = decoded["sub"]
    except Exception as e:
        print("❌ Error al decodificar token:", e)
        return jsonify({"ok": False, "msg": "Token inválido o expirado"}), 400

    users = get_users_collection()
    user = users.find_one({"correo": correo})
    if not user:
        return jsonify({"ok": False, "msg": "Usuario no encontrado"}), 404

    if user.get("verificado", False):
        return jsonify({"ok": True, "msg": "La cuenta ya estaba verificada"}), 200

    users.update_one({"_id": user["_id"]}, {"$set": {"verificado": True}})
    print("✅ Cuenta verificada correctamente")
    return jsonify({"ok": True, "msg": "Cuenta verificada correctamente"}), 200

# REENVIAR VERIFICACIÓN
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

    nuevo_token = create_access_token(identity=correo, expires_delta=timedelta(hours=24))
    users.update_one(
        {"_id": user["_id"]}, 
        {"$set": {"token_verificacion": nuevo_token}})

    try:
        enviar_correo_verificacion(correo, user["nombre"], nuevo_token)
    except Exception as e:
        print("❌ Error al reenviar correo:", e)

    return jsonify({"ok": True, "msg": "Se envió un nuevo correo de verificación"}), 200


# RECUPERAR CONTRASEÑA (SOLICITAR RESET)
def solicitar_reset_password(data):
    correo = data.get("correo")
    if not correo:
        return jsonify({"ok": False, "msg": "Correo requerido"}), 400

    users = get_users_collection()
    user = users.find_one({"correo": correo})
    if not user:
        return jsonify({"ok": False, "msg": "Usuario no encontrado"}), 404

    token_reset = create_access_token(identity=correo, expires_delta=timedelta(minutes=30))
    try:
        enviar_correo_reset(correo, user["nombre"], token_reset)
    except Exception as e:
        print("❌ Error al enviar correo reset:", e)

    return jsonify({"ok": True, "msg": "Correo de recuperación enviado"}), 200


# CONFIRMAR RESET PASSWORD
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


# CAMBIO DE CONTRASEÑA (USUARIO LOGUEADO)
@jwt_required()
def cambiar_password(data):
    user_id = get_jwt_identity()
    actual = data.get("actual")
    nueva = data.get("nueva")
    confirmar = data.get("confirmar")

    if not all([actual, nueva, confirmar]):
        return jsonify({"ok": False, "msg": "Completa todos los campos"}), 400
    if nueva != confirmar:
        return jsonify({"ok": False, "msg": "Las contraseñas no coinciden"}), 400

    users = get_users_collection()
    user = users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"ok": False, "msg": "Usuario no encontrado"}), 404

    if not check_password_hash(user["password"], actual):
        return jsonify({"ok": False, "msg": "La contraseña actual no es correcta"}), 401

    if (
        len(nueva) < 8
        or not re.search(r"[A-Z]", nueva)
        or not re.search(r"\d", nueva)
        or not re.search(r"[!@#$%^&*]", nueva)
    ):
        return jsonify({
            "ok": False,
            "msg": "La nueva contraseña no cumple los requisitos de seguridad."
        }), 400

    hashed_pw = generate_password_hash(nueva)
    users.update_one({"_id": user["_id"]}, {"$set": {"password": hashed_pw}})
    return jsonify({"ok": True, "msg": "Contraseña actualizada correctamente"}), 200

# ruta_usuario.py
from flask import Blueprint, request
from bson import ObjectId
from flask_api.modelo.modelo_usuario import get_users_collection
from flask_api.controlador.control_usuario import actualizar_perfil

usuario_bp = Blueprint("usuario", __name__, url_prefix="/usuario")

@usuario_bp.route("/perfil/<user_id>", methods=["GET"])
def get_perfil(user_id):
    col = get_users_collection()
    usuario = col.find_one({"_id": ObjectId(user_id)}, {"password": 0})  # nunca mandar password
    if not usuario:
        return {"ok": False, "msg": "Usuario no encontrado"}, 404

    # serializar ObjectId
    usuario["_id"] = str(usuario["_id"])
    return {"ok": True, "usuario": usuario}, 200


@usuario_bp.route("/perfil/<user_id>", methods=["PATCH"])
def update_perfil(user_id):
    data = request.get_json() or {}
    return actualizar_perfil(user_id, data)

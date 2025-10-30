# ruta_usuario.py
from flask import Blueprint, request
from bson import ObjectId
from flask_api.modelo.modelo_usuario import get_users_collection
from flask_api.controlador.control_usuario import actualizar_perfil
from flask_api.controlador.control_direcciones import agregar_direccion, listar_direcciones, eliminar_direccion, actualizar_direcciones

usuario_bp = Blueprint("usuario", __name__, url_prefix="/usuario")

@usuario_bp.route("/perfil/<user_id>", methods=["GET"])
def get_perfil(user_id):
    col = get_users_collection()
    usuario = col.find_one({"_id": ObjectId(user_id)}, {"password": 0})  # nunca mandar password
    if not usuario:
        return {"ok": False, "msg": "Usuario no encontrado"}, 404


    usuario["_id"] = str(usuario["_id"])
   
    return {"ok": True, "usuario": usuario}, 200


@usuario_bp.route("/perfil/<user_id>", methods=["PATCH"])
def update_perfil(user_id):
    data = request.get_json() or {}
    return actualizar_perfil(user_id, data)

@usuario_bp.route("/<user_id>/direcciones", methods=["GET"])
def obtener_direcciones(user_id):
    return listar_direcciones(user_id)

@usuario_bp.route("/direcciones/<dir_id>", methods=["PATCH"])
def editar_direccion(dir_id):
    data = request.get_json() or {}
    user_id = data.get("user_id") 
    if not user_id:
        return jsonify({"ok": False, "msg": "ID de usuario requerido para editar"}), 400

    # Corregir el orden de la llamada: user_id, dir_id, data
    return actualizar_direcciones(user_id, dir_id, data)

@usuario_bp.route("/<user_id>/direcciones", methods=["POST"])
def crear_direccion(user_id):
    data = request.get_json() or {}
    return agregar_direccion(user_id, data)

@usuario_bp.route("/direcciones/<dir_id>", methods=["DELETE"])
def borrar_direccion(dir_id):
    return eliminar_direccion(dir_id)
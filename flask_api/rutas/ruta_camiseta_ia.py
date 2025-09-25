from flask import Blueprint, request, jsonify
from bson import ObjectId
from bson.errors import InvalidId

from flask_api.controlador.control_camiseta_ia import generar_camiseta_ia, guardar_camiseta_seleccionada
from flask_api.modelo.modelo_camiseta_ia import listar_camisetas

ruta_camiseta_ia = Blueprint("ruta_camiseta_ia", __name__)

@ruta_camiseta_ia.route("/api/ia/camiseta_ia", methods=["POST"])
def generar():
    data = request.get_json()
    user_id = data.get("userId")
    atributos = data.get("atributos", {})

    if not user_id:
        return jsonify({"error": "Falta userId"}), 401
    try:
        ObjectId(user_id)
    except (InvalidId, TypeError):
        return jsonify({"error": "userId inválido"}), 400

    result = generar_camiseta_ia(atributos, user_id)
    return jsonify(result), 200


@ruta_camiseta_ia.route("/api/ia/camiseta_ia/guardar", methods=["POST"])
def guardar():
    data = request.get_json()
    user_id = data.get("userId")
    prompt = data.get("prompt")
    image_base64 = data.get("image")
    atributos = data.get("atributos", {})   

    if not user_id or not image_base64:
        return jsonify({"error": "Faltan parámetros"}), 400

    result = guardar_camiseta_seleccionada(user_id, prompt, image_base64, atributos)
    return jsonify(result), 200


@ruta_camiseta_ia.route("/api/ia/camiseta_ia/listar", methods=["GET"])
def listar():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Falta user_id"}), 401
    try:
        ObjectId(user_id)
    except (InvalidId, TypeError):
        return jsonify({"error": "userId inválido"}), 400

    docs = listar_camisetas(user_id)
    return jsonify({"camisetas": docs}), 200

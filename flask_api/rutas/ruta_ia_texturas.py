# flask_api/rutas/ruta_ia_texturas.py
from flask import Blueprint, request, jsonify
from bson import ObjectId
from bson.errors import InvalidId
from flask_api.controlador.control_ia_texturas import generar_textura
from flask_api.modelo.modelo_ia_texturas import listar_texturas

ruta_ia_texturas = Blueprint("ruta_ia_texturas", __name__)

@ruta_ia_texturas.route("/api/ia/generar_textura", methods=["POST"])
def generar_textura_route():
    data = request.get_json()
    prompt_textura = data.get("prompt_textura")
    side = data.get("side", "delantera")
    user_id = data.get("userId", "anon")

    if not prompt_textura:
        return jsonify({"error": "Falta prompt_textura"}), 400

    result = generar_textura(prompt_textura, user_id, side)

    if "error" in result:
        return jsonify(result), 500

    return jsonify(result), 200


@ruta_ia_texturas.route("/api/ia/texturas", methods=["GET"])
def listar_texturas_route():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Falta user_id"}), 400
    try:
        ObjectId(user_id)
    except (InvalidId, TypeError):
        return jsonify({"error": "user_id inválido"}), 400

    texturas = listar_texturas(user_id)
    return jsonify({"texturas": texturas}), 200

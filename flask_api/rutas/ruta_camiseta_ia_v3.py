# flask_api/ruta/ruta_camiseta_ia_v3.py
from flask import Blueprint, request, jsonify
from flask_api.controlador.control_camiseta_ia_v3 import generar_camiseta_v3

ruta_camiseta_ia_v3 = Blueprint("ruta_camiseta_ia_v3", __name__)

@ruta_camiseta_ia_v3.route("/api/ia/generar_camiseta_v3", methods=["POST"])
def generar_camiseta():
    data = request.get_json()
    user_id = data.get("userId")
    categoria_id = data.get("categoria_id")
    atributos = data
    try:
        result = generar_camiseta_v3(categoria_id, atributos, user_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

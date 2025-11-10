# flask_api/ruta/ruta_pantaloneta_ia_v1.py
from flask import Blueprint, request, jsonify
from flask_api.controlador.control_pantaloneta_ia_v1 import generar_pantaloneta_v1

ruta_pantaloneta_ia_v1 = Blueprint("ruta_pantaloneta_ia_v1", __name__)


@ruta_pantaloneta_ia_v1.route("/api/ia/generar_pantaloneta_v1", methods=["POST"])
def generar_pantaloneta():
    """
    Endpoint para generar una pantaloneta deportiva con IA
    """
    data = request.get_json()
    user_id = data.get("userId")
    categoria_id = data.get("categoria_id", "pantaloneta_ia_v1")
    atributos = data
    
    try:
        result = generar_pantaloneta_v1(categoria_id, atributos, user_id)
        return jsonify(result)
    except Exception as e:
        print(f"❌ Error en endpoint generar_pantaloneta: {e}")
        return jsonify({"error": str(e)}), 500

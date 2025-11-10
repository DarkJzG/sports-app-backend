# flask_api/ruta/ruta_conjunto_externo_ia_v1.py
from flask import Blueprint, request, jsonify
from flask_api.controlador.control_conjunto_externo_ia_v1 import generar_conjunto_externo_v1

ruta_conjunto_externo_ia_v1 = Blueprint("ruta_conjunto_externo_ia_v1", __name__)


@ruta_conjunto_externo_ia_v1.route("/api/ia/generar_conjunto_externo_v1", methods=["POST"])
def generar_conjunto_externo():
    """
    Endpoint para generar un conjunto deportivo externo (chaqueta + pantalón) con IA
    """
    data = request.get_json()
    user_id = data.get("userId")
    categoria_id = data.get("categoria_id", "conjunto_externo_ia_v1")
    atributos = data
    
    try:
        result = generar_conjunto_externo_v1(categoria_id, atributos, user_id)
        return jsonify(result)
    except Exception as e:
        print(f"❌ Error en endpoint generar_conjunto_externo: {e}")
        return jsonify({"error": str(e)}), 500

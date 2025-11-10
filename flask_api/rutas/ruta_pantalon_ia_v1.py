# flask_api/ruta/ruta_pantalon_ia_v1.py
from flask import Blueprint, request, jsonify
from flask_api.controlador.control_pantalon_ia_v1 import generar_pantalon_v1

ruta_pantalon_ia_v1 = Blueprint("ruta_pantalon_ia_v1", __name__)


@ruta_pantalon_ia_v1.route("/api/ia/generar_pantalon_v1", methods=["POST"])
def generar_pantalon():
    """
    Endpoint para generar un pantalón deportivo con IA
    """
    data = request.get_json()
    user_id = data.get("userId")
    categoria_id = data.get("categoria_id", "pantalon_ia_v1")
    atributos = data
    
    try:
        result = generar_pantalon_v1(categoria_id, atributos, user_id)
        return jsonify(result)
    except Exception as e:
        print(f"❌ Error en endpoint generar_pantalon: {e}")
        return jsonify({"error": str(e)}), 500

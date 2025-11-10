# flask_api/rutas/ruta_camiseta_huggingface_v3.py
from flask import Blueprint, request, jsonify
from flask_api.controlador.control_camiseta_huggingface_v3 import generar_camiseta_huggingface_v3

ruta_camiseta_huggingface_v3 = Blueprint("ruta_camiseta_huggingface_v3", __name__)

@ruta_camiseta_huggingface_v3.route("/api/ia/generar_camiseta_huggingface_v3", methods=["POST"])
def generar_camiseta():
    """
    Endpoint para generar camisetas usando Hugging Face.
    Recibe los mismos datos que los otros endpoints de generación.
    """
    try:
        data = request.get_json()
        
        # Validar datos básicos
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400
        
        user_id = data.get("userId")
        categoria_id = data.get("categoria_id", "camiseta_ia_v3")
        
        # Llamar al controlador
        result = generar_camiseta_huggingface_v3(categoria_id, data, user_id)
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Error en endpoint generar_camiseta_huggingface: {e}")
        return jsonify({"error": str(e)}), 500

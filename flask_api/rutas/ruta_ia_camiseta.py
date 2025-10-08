# flask_api/rutas/ruta_ia_camiseta.py
from flask import Blueprint, request, jsonify
from bson import ObjectId
from bson.errors import InvalidId
from flask_api.controlador.control_ia_camiseta import generar_camiseta

ruta_ia_camiseta = Blueprint("ruta_ia_camiseta", __name__)

@ruta_ia_camiseta.route("/api/ia/generar_camiseta_v2", methods=["POST"])
def generar_camiseta_route():
    try:
        data = request.get_json(force=True)  # 🔹 aseguramos que siempre llega json
        user_id = data.get("userId")
        categoria_id = data.get("categoria_id")  # 🔹 definimos aquí
        atributos = data.get("atributos", {})

        if not user_id or not categoria_id:
            return jsonify({"error": "Faltan IDs"}), 400

        # Validamos IDs (solo user_id es crítico para guardar en DB)
        try:
            ObjectId(user_id)
        except (InvalidId, TypeError):
            return jsonify({"error": "userId inválido"}), 400

        # ⚠️ Si quieres permitir pruebas con categoria_id "dummy", comenta esta parte
        try:
            ObjectId(categoria_id)
        except (InvalidId, TypeError):
            if categoria_id != "dummy":  # 🔹 permite dummy para pruebas
                return jsonify({"error": "categoria_id inválido"}), 400

        result = generar_camiseta(categoria_id, atributos, user_id)
        return jsonify(result), (200 if "error" not in result else 500)

    except Exception as e:
        import traceback
        print("❌ Error en generar_camiseta_route:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

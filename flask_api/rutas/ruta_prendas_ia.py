# flask_api/rutas/ruta_prendas_ia.py
from flask import Blueprint, request, jsonify, current_app

prendas_ia_bp = Blueprint("prendas_ia", __name__, url_prefix="/prendas_ia")

@prendas_ia_bp.route("", methods=["GET"])
def get_prendas_ia():
    user_id = request.args.get("userId")
    if not user_id:
        return jsonify({"ok": False, "msg": "Falta userId"}), 400
    
    prendas = list(current_app.mongo.db.prendas.find({"userId": user_id}))
    for p in prendas:
        p["_id"] = str(p["_id"])
    return jsonify({"ok": True, "prendas": prendas})

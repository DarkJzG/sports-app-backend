# flask_api/rutas/ruta_ia_prendas.py
from flask import Blueprint, request, jsonify
from bson.errors import InvalidId
from bson import ObjectId

from flask_api.controlador.control_ia_prendas import generar_imagen, generar_pdf
from flask_api.modelo.modelo_ia_prendas import listar_prendas

ruta_ia_prendas = Blueprint("ruta_ia_prendas", __name__)

# Generar imagen + ficha + costo
@ruta_ia_prendas.route("/api/ia/generar_prendas", methods=["POST"])
def generar_prenda():
    data = request.get_json()
    tipo_prenda = data.get("tipo_prenda")
    atributos = data.get("atributos", {})
    user_id = data.get("userId")

    if not tipo_prenda:
        return jsonify({"error": "Falta tipo_prenda"}), 400
    if not user_id:
        return jsonify({"error": "Falta userId"}), 401

    try:
        ObjectId(user_id)
    except (InvalidId, TypeError):
        return jsonify({"error": "userId inválido"}), 400

    result = generar_imagen(tipo_prenda, atributos, user_id)
    return jsonify(result), 200

# Generar PDF ficha técnica
@ruta_ia_prendas.route("/api/ia/ficha_tecnica", methods=["POST"])
def ficha_pdf():
    data = request.get_json()
    ficha = data.get("ficha", {})
    imagen_b64 = data.get("imagen")
    image_url = data.get("imageUrl")

    pdf_b64 = generar_pdf(ficha, imagen_b64, image_url)
    return jsonify({"ok": True, "pdf_base64": pdf_b64}), 200

# Listar prendas
@ruta_ia_prendas.route("/prendas_ia/listar", methods=["GET"])
def listar():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Falta user_id"}), 401
    try:
        ObjectId(user_id)
    except (InvalidId, TypeError):
        return jsonify({"error": "userId inválido"}), 400

    prendas = listar_prendas(user_id)
    return jsonify({"prendas": prendas}), 200

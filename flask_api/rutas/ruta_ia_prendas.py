# flask_api/rutas/ruta_ia_prendas.py
from flask import Blueprint, current_app, request, jsonify
from bson.errors import InvalidId
from bson import ObjectId

from flask_api.controlador.control_ia_prendas import (
    generar_imagen,
    generar_pdf,
    guardar_prenda_seleccionada
)
from flask_api.modelo.modelo_ia_prendas import listar_prendas

ruta_ia_prendas = Blueprint("ruta_ia_prendas", __name__)

# ---------------------------------------------------------
# Generar imagen + ficha técnica + costo
# Compatible con FormCamiseta y GuiaCamiseta
# ---------------------------------------------------------
@ruta_ia_prendas.route("/api/ia/generar_prendas", methods=["POST"])
def generar_prenda():
    data = request.get_json()
    tipo_prenda = data.get("tipo_prenda", "camiseta")  # por defecto camiseta
    atributos = data.get("atributos", {})
    user_id = data.get("userId")

    if not user_id:
        return jsonify({"error": "Falta userId"}), 401

    try:
        ObjectId(user_id)
    except (InvalidId, TypeError):
        return jsonify({"error": "userId inválido"}), 400

    result = generar_imagen(tipo_prenda, atributos, user_id)
    return jsonify(result), (200 if "error" not in result else 500)


# ---------------------------------------------------------
# Guardar selección de una imagen generada
# (caso GuiaCamiseta.jsx que muestra varias opciones)
# ---------------------------------------------------------
@ruta_ia_prendas.route("/api/ia/prendas/guardar", methods=["POST"])
def guardar_prenda():
    data = request.get_json()
    user_id = data.get("userId")
    prompt = data.get("prompt")
    image_base64 = data.get("image")
    atributos = data.get("atributos", {})

    if not user_id or not image_base64:
        return jsonify({"error": "Faltan parámetros"}), 400

    try:
        ObjectId(user_id)
    except (InvalidId, TypeError):
        return jsonify({"error": "userId inválido"}), 400

    result = guardar_prenda_seleccionada(user_id, prompt, image_base64, atributos)
    return jsonify(result), (200 if result.get("ok") else 500)


# ---------------------------------------------------------
# Generar PDF ficha técnica (compatible con ambos flujos)
# ---------------------------------------------------------
@ruta_ia_prendas.route("/api/ia/ficha_tecnica", methods=["POST"])
def ficha_pdf():
    data = request.get_json()
    ficha = data.get("ficha", {})
    imagen_b64 = data.get("imagen")
    image_url = data.get("imageUrl")

    pdf_b64 = generar_pdf(ficha, imagen_b64, image_url)
    return jsonify({"ok": True, "pdf_base64": pdf_b64}), 200


# ---------------------------------------------------------
# Listar prendas de un usuario
# ---------------------------------------------------------
@ruta_ia_prendas.route("/api/ia/prendas/listar", methods=["GET"])
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


# ---------------------------------------------------------
# Endpoint para verificar la URL de Stable Diffusion
# ---------------------------------------------------------
@ruta_ia_prendas.route("/api/ia/check_stable", methods=["GET"])
def check_stable():
    return jsonify({
        "stable_url": current_app.config["STABLE_URL"]
    })

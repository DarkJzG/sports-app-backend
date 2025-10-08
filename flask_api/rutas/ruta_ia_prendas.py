# flask_api/rutas/ruta_ia_prendas.py
from flask import Blueprint, current_app, request, jsonify
from bson.errors import InvalidId
from bson import ObjectId


from flask_api.controlador.control_ia_prendas import (
    generar_imagen,
)
from flask_api.modelo.modelo_ia_prendas import (
    listar_prendas, 
    buscar_prenda, 
    eliminar_prenda, 
)

ruta_ia_prendas = Blueprint("ruta_ia_prendas", __name__)

# ---------------------------------------------------------
# Generar imagen + costo
# ---------------------------------------------------------
@ruta_ia_prendas.route("/api/ia/generar_prendas", methods=["POST"])
def generar_prenda():
    data = request.get_json()
    categoria_id = data.get("categoria_id")    # ✅ corregido
    categoria_prd = data.get("categoria_prd", "camiseta")
    atributos = data.get("atributos", {})
    user_id = data.get("userId")

    if not user_id:
        return jsonify({"error": "Falta userId"}), 401
    if not categoria_id:
        return jsonify({"error": "Falta categoria_id"}), 401

    try:
        ObjectId(user_id)
        ObjectId(categoria_id)   # ✅ validar también categoria_id
    except (InvalidId, TypeError):
        return jsonify({"error": "ID inválido"}), 400

    result = generar_imagen(categoria_id, categoria_prd, atributos, user_id)
    return jsonify(result), (200 if "error" not in result else 500)


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
# Obtener prenda por ID
# ---------------------------------------------------------
@ruta_ia_prendas.route("/api/ia/prendas/<prenda_id>", methods=["GET"])
def obtener_prenda(prenda_id):
    try:
        ObjectId(prenda_id)
    except (InvalidId, TypeError):
        return jsonify({"error": "ID inválido"}), 400

    prenda = buscar_prenda(prenda_id)
    if not prenda:
        return jsonify({"error": "Prenda no encontrada"}), 404
    return jsonify(prenda), 200

# ---------------------------------------------------------
# Eliminar prenda
# ---------------------------------------------------------
@ruta_ia_prendas.route("/api/ia/prendas/eliminar/<prenda_id>", methods=["DELETE"])
def eliminar(prenda_id):
    try:
        ObjectId(prenda_id)
    except (InvalidId, TypeError):
        return jsonify({"error": "ID inválido"}), 400

    ok = eliminar_prenda(prenda_id)
    return jsonify({"ok": ok}), (200 if ok else 404)

# ---------------------------------------------------------
# Endpoint para verificar la URL de Stable Diffusion
# ---------------------------------------------------------
@ruta_ia_prendas.route("/api/ia/check_stable", methods=["GET"])
def check_stable():
    return jsonify({
        "stable_url": current_app.config["STABLE_URL"]
    })


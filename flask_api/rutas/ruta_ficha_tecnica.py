# flask_api/rutas/ruta_ficha_tecnica.py
from flask import Blueprint, request, jsonify, current_app
from bson import ObjectId
from flask_api.modelo.modelo_ficha_tecnica import (
    guardar_ficha, buscar_ficha, listar_fichas, eliminar_ficha
)
from flask_api.controlador.control_ficha_tecnica import generar_ficha_tecnica_prueba
from reportlab.platypus import SimpleDocTemplate, PageBreak
import io, base64

ruta_ficha_tecnica = Blueprint("ruta_ficha_tecnica", __name__)

# Guardar ficha técnica independiente
@ruta_ficha_tecnica.route("/api/ficha/guardar", methods=["POST"])
def guardar():
    data = request.get_json()
    ficha_id = guardar_ficha(data)
    return jsonify({"ok": True, "ficha_id": ficha_id}), 201

# Obtener ficha técnica por ID
@ruta_ficha_tecnica.route("/api/ficha/<ficha_id>", methods=["GET"])
def obtener(ficha_id):
    try:
        ObjectId(ficha_id)
    except Exception:
        return jsonify({"error": "ID inválido"}), 400

    ficha = buscar_ficha(ficha_id)
    if not ficha:
        return jsonify({"error": "Ficha no encontrada"}), 404
    return jsonify(ficha), 200

# Listar fichas de un usuario
@ruta_ficha_tecnica.route("/api/ficha/listar", methods=["GET"])
def listar():
    user_id = request.args.get("user_id")
    if user_id:
        try:
            ObjectId(user_id)
        except Exception:
            return jsonify({"error": "user_id inválido"}), 400
    fichas = listar_fichas(user_id)
    return jsonify({"fichas": fichas}), 200

# Eliminar ficha técnica
@ruta_ficha_tecnica.route("/api/ficha/eliminar/<ficha_id>", methods=["DELETE"])
def eliminar(ficha_id):
    try:
        ObjectId(ficha_id)
    except Exception:
        return jsonify({"error": "ID inválido"}), 400

    ok = eliminar_ficha(ficha_id)
    return jsonify({"ok": ok}), (200 if ok else 404)

# Generar PDF de una ficha técnica existente
@ruta_ficha_tecnica.route("/api/ficha/<ficha_id>/pdf", methods=["GET"])
def generar_pdf(ficha_id):
    ficha = buscar_ficha(ficha_id)
    
    if not ficha:
        return jsonify({"error": "Ficha no encontrada"}), 404
    print("🟣 Ficha completa para PDF:", ficha)

    pdf_b64 = generar_ficha_tecnica_prueba(ficha)
    return jsonify({"ok": True, "pdf_base64": pdf_b64}), 200

# Generar PDF multipágina de todas las fichas de un pedido
@ruta_ficha_tecnica.route("/api/fichas/pedido/<pedido_id>/pdf", methods=["GET"])
def generar_pdf_pedido(pedido_id):
    db = current_app.mongo.db
    pedido = db.pedidos.find_one({"_id": ObjectId(pedido_id)})
    if not pedido:
        return jsonify({"error": "Pedido no encontrado"}), 404

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    all_elements = []

    # iterar items y buscar ficha
    for item in pedido.get("items", []):
        if "ficha_id" in item:
            ficha = buscar_ficha(item["ficha_id"])
            if ficha:
                elements = generar_ficha_tecnica_prueba(ficha, return_elements=True)
                all_elements.extend(elements)
                all_elements.append(PageBreak())

    if not all_elements:
        return jsonify({"error": "No hay fichas técnicas en este pedido"}), 404

    doc.build(all_elements)
    buffer.seek(0)
    pdf_b64 = base64.b64encode(buffer.read()).decode("utf-8")
    return jsonify({"ok": True, "pdf_base64": pdf_b64}), 200

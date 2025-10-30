# flask_api/rutas/ruta_pedido.py
import json
import cloudinary.uploader

from flask import Blueprint, request, jsonify, current_app
from flask_api.controlador.control_pedido import (
    mis_pedidos, listar_pedidos_admin, cambiar_estado_pedido,
    confirmar_pedido_transferencia, registrar_pago
)
from flask_api.modelo.modelo_ficha_tecnica import get_fichas_collection
from bson import ObjectId

pedido_bp = Blueprint("pedido", __name__, url_prefix="/pedido")


# GET /pedido/get/:id
@pedido_bp.route("/get/<pedido_id>", methods=["GET"])
def get_pedido(pedido_id):
    from flask_api.modelo.modelo_pedido import get_pedidos_collection, _serialize
    from bson import ObjectId

    col = get_pedidos_collection()
    pedido = col.find_one({"_id": ObjectId(pedido_id)})
    if not pedido:
        return {"ok": False, "msg": "Pedido no encontrado"}, 404
    return {"ok": True, "pedido": _serialize(pedido)}, 200


# GET /pedido/mis-pedidos/:userId?page=&limit=
@pedido_bp.route("/mis-pedidos/<userId>", methods=["GET"])
def mis_pedidos_route(userId):
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))
    return mis_pedidos(userId, page, limit)

# GET /pedido/all?estado=&userId=&page=&limit=   (ADMIN)
@pedido_bp.route("/all", methods=["GET"])
def listar_admin():
    estado = request.args.get("estado")
    q_user = request.args.get("userId")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))
    return listar_pedidos_admin(estado, q_user, page, limit)

# PATCH /pedido/<pedidoId>/estado  (ADMIN)
@pedido_bp.route("/<pedidoId>/estado", methods=["PATCH"])
def cambiar_estado(pedidoId):
    data = request.get_json() or {}
    nuevo_estado = data.get("estado")
    nota_admin = data.get("nota")
    fechaEntrega = data.get("fechaEntrega")
    return cambiar_estado_pedido(pedidoId, nuevo_estado, nota_admin, fechaEntrega)

@pedido_bp.route("/confirmar-transferencia/<userId>", methods=["POST"])
def confirmar_transferencia(userId):
    try:
        # Verificar si se envió un archivo
        if 'imagen' not in request.files:
            return jsonify({"ok": False, "msg": "No se ha proporcionado ninguna imagen"}), 400
            
        file = request.files['imagen']
        
        # Verificar que el archivo tenga un nombre
        if file.filename == '':
            return jsonify({"ok": False, "msg": "No se ha seleccionado ningún archivo"}), 400

        # Verificar que el archivo sea una imagen
        if not file.content_type.startswith('image/'):
            return jsonify({"ok": False, "msg": "El archivo debe ser una imagen"}), 400

        # Obtener los datos del formulario
        if 'data' not in request.form:
            return jsonify({"ok": False, "msg": "Datos del pedido no proporcionados"}), 400

        try:
            data = json.loads(request.form['data'])
        except json.JSONDecodeError:
            return jsonify({"ok": False, "msg": "Formato de datos inválido"}), 400

        # ✅ Subir la imagen a Cloudinary ANTES de procesar el pedido
        try:
            upload_result = cloudinary.uploader.upload(
                file,
                folder="transferencias",
                resource_type="image"
            )
            imagen_url = upload_result['secure_url']
            current_app.logger.info(f"Imagen subida a Cloudinary: {imagen_url}")
        except Exception as e:
            current_app.logger.error(f"Error al subir la imagen: {str(e)}")
            return jsonify({"ok": False, "msg": "Error al procesar la imagen"}), 500

        # ✅ Actualizar fichas técnicas si aplica
        for item in data.get("items", []):
            if item.get("ficha_id") and item.get("talla"):
                get_fichas_collection().update_one(
                    {"_id": ObjectId(item["ficha_id"])},
                    {"$set": {"talla": item["talla"]}}
                )

        # ✅ IMPORTANTE: Pasar los 3 parámetros a la función del controlador
        return confirmar_pedido_transferencia(userId, data, imagen_url)
        
    except Exception as e:
        current_app.logger.error(f"Error en confirmar transferencia: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"ok": False, "msg": "Error al procesar la solicitud"}), 500

        
# PATCH /pedido/<pedidoId>/pago/<pagoId>/aprobar
@pedido_bp.route("/<pedidoId>/pago/<pagoId>/aprobar", methods=["PATCH"])
def aprobar_pago_route(pedidoId, pagoId):
    from flask_api.controlador.control_pedido import aprobar_pago
    return aprobar_pago(pedidoId, pagoId)


# PATCH /pedido/<pedidoId>/pago/<pagoId>/rechazar
@pedido_bp.route("/<pedidoId>/pago/<pagoId>/rechazar", methods=["PATCH"])
def rechazar_pago_route(pedidoId, pagoId):
    from flask_api.controlador.control_pedido import rechazar_pago
    data = request.get_json() or {}
    motivo = data.get("motivo")
    return rechazar_pago(pedidoId, pagoId, motivo)


# POST /pedido/<pedidoId>/pago
@pedido_bp.route("/<pedidoId>/pago", methods=["POST"])
def registrar_pago_route(pedidoId):
    try:
        # Verificar si se envió un archivo
        if 'imagen' not in request.files:
            return jsonify({"ok": False, "msg": "No se ha proporcionado ninguna imagen"}), 400
            
        file = request.files['imagen']
        
        # Verificar que el archivo tenga un nombre
        if file.filename == '':
            return jsonify({"ok": False, "msg": "No se ha seleccionado ningún archivo"}), 400

        # Verificar que el archivo sea una imagen
        if not file.content_type.startswith('image/'):
            return jsonify({"ok": False, "msg": "El archivo debe ser una imagen"}), 400

        # Obtener los datos del formulario
        if 'data' not in request.form:
            return jsonify({"ok": False, "msg": "Datos del pago no proporcionados"}), 400

        try:
            data = json.loads(request.form['data'])
        except json.JSONDecodeError:
            return jsonify({"ok": False, "msg": "Formato de datos inválido"}), 400

        # Subir la imagen a Cloudinary
        try:
            upload_result = cloudinary.uploader.upload(
                file,
                folder="comprobantes_pago",
                resource_type="image"
            )
            # Agregar la URL de la imagen a los datos del pago
            data['imagenComprobante'] = upload_result['secure_url']
        except Exception as e:
            current_app.logger.error(f"Error al subir la imagen: {str(e)}")
            return jsonify({"ok": False, "msg": "Error al procesar la imagen"}), 500

        # Procesar el pago con los datos y la URL de la imagen
        return registrar_pago(pedidoId, data)
        
    except Exception as e:
        current_app.logger.error(f"Error en registrar pago: {str(e)}")
        return jsonify({"ok": False, "msg": "Error al procesar la solicitud"}), 500
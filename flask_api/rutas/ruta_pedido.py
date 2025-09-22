# flask_api/rutas/ruta_pedido.py
from flask import Blueprint, request
from flask_api.controlador.control_pedido import (
    mis_pedidos, listar_pedidos_admin, cambiar_estado_pedido,
    confirmar_pedido_transferencia, registrar_pago
)

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
    return cambiar_estado_pedido(pedidoId, nuevo_estado, nota_admin)

@pedido_bp.route("/confirmar-transferencia/<userId>", methods=["POST"])
def confirmar_transferencia(userId):
    data = request.get_json() or {}
    return confirmar_pedido_transferencia(userId, data)

# POST /pedido/<pedidoId>/pago
@pedido_bp.route("/<pedidoId>/pago", methods=["POST"])
def registrar_pago_route(pedidoId):
    data = request.get_json() or {}
    return registrar_pago(pedidoId, data)

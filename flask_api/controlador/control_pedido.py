# flask_api/controlador/control_pedido.py
from flask import jsonify
from bson import ObjectId
from flask_api.modelo.modelo_pedido import (
    _now_utc, build_pedido_doc, insert_pedido, find_pedidos_by_user, find_all_pedidos,
    update_pedido_status, ESTADOS_PEDIDO
)

from flask_api.modelo.modelo_pedido import get_pedidos_collection

def registrar_pago(pedido_id: str, data: dict):
    """
    data = { "monto": float, "referencia": str, "presencial": bool }
    """
    col = get_pedidos_collection()
    pedido = col.find_one({"_id": ObjectId(pedido_id)})
    if not pedido:
        return jsonify({"ok": False, "msg": "Pedido no encontrado"}), 404

    monto = float(data.get("monto", 0))
    if monto <= 0:
        return jsonify({"ok": False, "msg": "Monto inválido"}), 400

    nuevo_saldo = round(float(pedido["saldoPendiente"]) - monto, 2)
    estado = "pagado_total" if nuevo_saldo <= 0 else "pagado_parcial"

    col.update_one(
        {"_id": pedido["_id"]},
        {
            "$set": {
                "montoPagado": float(pedido["montoPagado"]) + monto,
                "saldoPendiente": max(nuevo_saldo, 0),
                "estado": estado,
                "updatedAt": _now_utc(),
            },
            "$push": {
                "referenciasPago": {
                    "monto": monto,
                    "referencia": data.get("referencia"),
                    "presencial": data.get("presencial", False),
                    "fecha": _now_utc(),
                },
                "timeline": {"evento": "pago_registrado", "estado": estado, "ts": _now_utc()},
            },
        },
    )
    return jsonify({"ok": True, "msg": "Pago registrado", "nuevoEstado": estado}), 200


def _validar_payload_confirmacion(data: dict):
    requeridos = ["items", "direccionEnvio", "metodoPago", "costos"]
    for k in requeridos:
        if k not in data:
            return f"Falta el campo '{k}'"
    if not isinstance(data["items"], list) or len(data["items"]) == 0:
        return "La lista de 'items' debe tener al menos 1 elemento"
    
    campos_item = ["productId", "nombre", "cantidad", "precioUnitario"]
    for i, it in enumerate(data["items"]):
        for c in campos_item:
            if c not in it:
                return f"Item {i} sin campo requerido '{c}'"
            
        if int(it["cantidad"]) <= 0:
            return f"Item {i} con cantidad inválida"
        
    if isinstance(data["direccionEnvio"], dict):
        if "tipoEnvio" not in data["direccionEnvio"]:
            return "La dirección de envío requiere el campo 'tipoEnvio' (domicilio o retiro)"
    elif not isinstance(data["direccionEnvio"], str):
        return "La dirección de envío debe ser un objeto o texto válido"

    return None

def confirmar_pedido_transferencia(user_id: str, data: dict):
    err = _validar_payload_confirmacion(data)
    if err:
        return jsonify({"ok": False, "msg": err}), 400

    pedido_doc = build_pedido_doc(user_id, data)
    pedido_id = insert_pedido(pedido_doc)
    return jsonify({"ok": True, "msg": "Pedido creado", "pedidoId": pedido_id}), 201


def mis_pedidos(user_id: str, page: int = 1, limit: int = 20):
    pedidos, total = find_pedidos_by_user(user_id, page, limit)
    return jsonify({
        "ok": True,
        "total": total,
        "page": page,
        "limit": limit,
        "pedidos": pedidos
    }), 200

def listar_pedidos_admin(estado: str = None, q_user: str = None, page: int = 1, limit: int = 20):
    filt = {}
    if estado:
        if estado not in ESTADOS_PEDIDO:
            return jsonify({"ok": False, "msg": "Estado inválido"}), 400
        filt["estado"] = estado
    if q_user:
        try:
            filt["userId"] = ObjectId(q_user)
        except Exception:
            return jsonify({"ok": False, "msg": "userId inválido en filtro"}), 400

    pedidos, total = find_all_pedidos(filt, page, limit)
    return jsonify({
        "ok": True,
        "total": total,
        "page": page,
        "limit": limit,
        "pedidos": pedidos
    }), 200

def cambiar_estado_pedido(pedido_id: str, nuevo_estado: str, nota_admin: str = None):
    try:
        ok = update_pedido_status(pedido_id, nuevo_estado, nota_admin)
    except ValueError as e:
        return jsonify({"ok": False, "msg": str(e)}), 400

    if not ok:
        return jsonify({"ok": False, "msg": "Pedido no encontrado"}), 404

    return jsonify({"ok": True, "msg": "Estado actualizado"}), 200

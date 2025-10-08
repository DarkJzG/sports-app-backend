# flask_api/controlador/control_pedido.py
from flask import jsonify, current_app
from bson import ObjectId
from flask_api.modelo.modelo_pedido import (
    _now_utc, build_pedido_doc, insert_pedido, find_pedidos_by_user, find_all_pedidos,
    update_pedido_status, ESTADOS_PEDIDO, _serialize
)

from flask_api.modelo.modelo_pedido import get_pedidos_collection

def registrar_pago(pedido_id: str, data: dict):
    """
    data = { 
        "monto": float, 
        "referencia": str, 
        "presencial": bool,
        "imagenComprobante": str  # URL de la imagen del comprobante
    }
    """
    from bson import ObjectId
    col = get_pedidos_collection()
    
    # Validar que el pedido exista
    pedido = col.find_one({"_id": ObjectId(pedido_id)})
    if not pedido:
        return jsonify({"ok": False, "msg": "Pedido no encontrado"}), 404

    # Validar campos requeridos
    if not all(k in data for k in ["monto", "referencia"]):
        return jsonify({"ok": False, "msg": "Faltan campos requeridos"}), 400

    try:
        monto = float(data["monto"])
        if monto <= 0:
            return jsonify({"ok": False, "msg": "Monto inválido"}), 400

        # Calcular nuevo saldo
        saldo_actual = float(pedido.get("saldoPendiente", 0))
        monto_pagado = float(pedido.get("montoPagado", 0))
        total_pedido = float(pedido["costos"]["total"])
        
        if monto > saldo_actual:
            return jsonify({"ok": False, "msg": "El monto excede el saldo pendiente"}), 400

        nuevo_saldo = round(saldo_actual - monto, 2)
        nuevo_monto_pagado = round(monto_pagado + monto, 2)
        
        # Determinar el nuevo estado
        if nuevo_saldo <= 0:
            nuevo_estado = "pagado_total"
        else:
            nuevo_estado = "pagado_parcial"

        # Crear objeto de pago
        nuevo_pago = {
            "monto": monto,
            "fecha": _now_utc(),
            "referencia": data["referencia"],
            "comprobante": data.get("imagenComprobante", ""),
            "tipo": "completo" if nuevo_estado == "pagado_total" else "parcial",
            "estado": "aprobado",
            "nota": data.get("nota", "Pago registrado")
        }

        # Actualizar el pedido
        update_data = {
            "$set": {
                "montoPagado": nuevo_monto_pagado,
                "saldoPendiente": max(nuevo_saldo, 0),
                "estado": nuevo_estado,
                "updatedAt": _now_utc(),
                "referenciaPago": data["referencia"],  # Mantener para compatibilidad
                "comprobanteTransferencia": data.get("imagenComprobante", "")  # Mantener para compatibilidad
            },
            "$push": {
                "pagos": nuevo_pago,
                "timeline": {
                    "evento": "pago_registrado",
                    "estado": nuevo_estado,
                    "ts": _now_utc(),
                    "nota": f"Pago registrado por ${monto:.2f}" + 
                            (f" (Referencia: {data['referencia']})" if data.get("referencia") else "")
                }
            }
        }

        col.update_one({"_id": ObjectId(pedido_id)}, update_data)

        # Obtener el pedido actualizado
        pedido_actualizado = col.find_one({"_id": ObjectId(pedido_id)})
        
        return jsonify({
            "ok": True,
            "msg": "Pago registrado exitosamente",
            "pedido": _serialize(pedido_actualizado)
        })

    except (ValueError, TypeError) as e:
        return jsonify({"ok": False, "msg": "Error en el formato de los datos"}), 400
    except Exception as e:
        current_app.logger.error(f"Error al registrar pago: {str(e)}")
        return jsonify({"ok": False, "msg": "Error al procesar el pago"}), 500

def _validar_payload_confirmacion(data: dict):
    requeridos = ["items", "direccionEnvio", "metodoPago", "costos", "tipoPago"]
    for k in requeridos:
        if k not in data:
            return f"Falta el campo '{k}'"
            
    if not isinstance(data["items"], list) or len(data["items"]) == 0:
        return "La lista de 'items' debe tener al menos 1 elemento"
    
    # Validar campos requeridos en cada ítem
    campos_item = ["productId", "nombre", "cantidad", "precioUnitario", "talla", "color", "imagen"]
    for i, it in enumerate(data["items"]):
        for c in campos_item:
            if c not in it:
                return f"Item {i} sin campo requerido '{c}'"
            
        if int(it["cantidad"]) <= 0:
            return f"Item {i} con cantidad inválida"
        
        if it.get("tipo") == "ia_prenda":
                if "ficha_id" not in it or not it["ficha_id"]:
                    return f"Item {i} (ia_prenda) requiere 'ficha_id'"
    
    # Validar dirección de envío
    if not isinstance(data["direccionEnvio"], dict):
        return "La dirección de envío debe ser un objeto"
        
    campos_direccion = ["tipoEnvio", "nombre", "direccion_principal", "ciudad", 
                       "provincia", "pais", "telefono", "codigo_postal"]
    
    if data["direccionEnvio"]["tipoEnvio"] == "domicilio":
        for campo in campos_direccion:
            if campo not in data["direccionEnvio"] or not data["direccionEnvio"][campo]:
                return f"Campo requerido en dirección de envío: {campo}"
    
    # Validar costos
    campos_costo = ["subtotal", "envio", "total", "impuestos"]
    for campo in campos_costo:
        if campo not in data["costos"] or not isinstance(data["costos"][campo], (int, float)):
            return f"Costo inválido o faltante: {campo}"
    
    # Validar tipo de pago
    if data["tipoPago"] not in ["completo", "anticipo"]:
        return "Tipo de pago inválido. Debe ser 'completo' o 'anticipo'"
    
    return None

def confirmar_pedido_transferencia(user_id: str, data: dict):
    # Validar el payload
    err = _validar_payload_confirmacion(data)
    if err:
        return jsonify({"ok": False, "msg": err}), 400

    try:
        # Verificar que la imagen de transferencia esté presente
        if "imagenTransferencia" not in data:
            return jsonify({"ok": False, "msg": "Se requiere la imagen de la transferencia"}), 400

        # Construir el documento del pedido con la URL de la imagen
        pedido_doc = build_pedido_doc(user_id, data)
        
        # Insertar el pedido en la base de datos
        pedido_id = insert_pedido(pedido_doc)
        
        # Si el pago es completo, actualizar el estado a "pagado_total"
        if data.get("tipoPago") == "completo":
            from flask_api.modelo.modelo_pedido import update_pedido_status
            update_pedido_status(pedido_id, "pagado_total", "Pago completo recibido")
        
        return jsonify({
            "ok": True, 
            "msg": "Pedido creado exitosamente", 
            "pedidoId": pedido_id
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error al confirmar pedido: {str(e)}")
        return jsonify({
            "ok": False,
            "msg": f"Error al procesar el pedido: {str(e)}"
        }), 500


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

def cambiar_estado_pedido(pedido_id: str, nuevo_estado: str, nota_admin: str = None, fechaEntrega: str = None):
    try:
        ok = update_pedido_status(pedido_id, nuevo_estado, nota_admin, fechaEntrega)
    except ValueError as e:
        return jsonify({"ok": False, "msg": str(e)}), 400

    if not ok:
        return jsonify({"ok": False, "msg": "Pedido no encontrado"}), 404

    return jsonify({"ok": True, "msg": "Estado actualizado"}), 200


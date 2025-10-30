from flask import jsonify, current_app
from bson import ObjectId
from flask_api.modelo.modelo_pedido import (
    _now_utc, 
    build_pedido_doc, 
    insert_pedido, 
    find_pedidos_by_user, 
    find_all_pedidos,
    update_pedido_status, 
    ESTADOS_PEDIDO,
    ESTADOS_PAGO,
    _serialize,
    get_pedidos_collection,
    calcular_estado_pago,
    calcular_totales_pago,
    calcular_info_pago
)
from flask_api.modelo.modelo_usuario import get_users_collection



def _validar_payload_confirmacion(data: dict):
    """
    Valida el payload de confirmación de pedido.
    
    Returns:
        str: Mensaje de error si hay problema, None si todo está bien
    """
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
            it["ficha_id"] = it.get("ficha_id") or None
    
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


def aprobar_pago(pedido_id: str, pago_id: str):
    """
    Aprueba un pago específico y recalcula el estado de pago del pedido.
    """
    col = get_pedidos_collection()
    
    # Buscar el pedido
    pedido = col.find_one({"_id": ObjectId(pedido_id)})
    if not pedido:
        return jsonify({"ok": False, "msg": "Pedido no encontrado"}), 404
    
    # Buscar el pago en el array
    pago_encontrado = None
    for i, pago in enumerate(pedido.get("pagos", [])):
        if i == int(pago_id):
            pago_encontrado = pago
            pago_index = i
            break
    
    if not pago_encontrado:
        return jsonify({"ok": False, "msg": "Pago no encontrado"}), 404
    
    # Verificar si ya está aprobado
    if pago_encontrado.get("estado") == "aprobado":
        return jsonify({"ok": False, "msg": "El pago ya está aprobado"}), 400
    
    # Actualizar el estado del pago
    col.update_one(
        {"_id": ObjectId(pedido_id)},
        {
            "$set": {
                f"pagos.{pago_index}.estado": "aprobado",
                f"pagos.{pago_index}.fechaAprobacion": _now_utc(),
                "updatedAt": _now_utc()
            }
        }
    )
    
    # Obtener el pedido actualizado
    pedido_actualizado = col.find_one({"_id": ObjectId(pedido_id)})
    
    # ✅ Recalcular el estado de pago
    infoPago = calcular_info_pago(pedido_actualizado)
    nuevo_estado_pago = infoPago["estado_pago"]
    totales = infoPago
    
    # Actualizar estado de pago en el documento
    update_data = {
        "$set": {
            "estadoPago": nuevo_estado_pago,
            "infoPago": infoPago,  # ✅ Guardar también infoPago
            "updatedAt": _now_utc()
        },
        "$push": {
            "timeline": {
                "evento": "pago_aprobado",
                "estadoPago": nuevo_estado_pago,
                "ts": _now_utc(),
                "nota": f"Pago de ${float(pago_encontrado['monto']):.2f} aprobado. " +
                    f"Total pagado: ${totales['total_pagado']:.2f} de ${totales['total_pedido']:.2f} " +
                    f"({totales['porcentaje_pagado']}%)"
            }
        }
    }
    
    col.update_one({"_id": ObjectId(pedido_id)}, update_data)
    
    # Obtener el pedido final
    pedido_final = col.find_one({"_id": ObjectId(pedido_id)})
    
    return jsonify({
        "ok": True,
        "msg": "Pago aprobado exitosamente",
        "pedido": _serialize(pedido_final)
    }), 200


def rechazar_pago(pedido_id: str, pago_id: str, motivo: str = None):
    """
    Rechaza un pago específico.
    """
    col = get_pedidos_collection()
    
    # Buscar el pedido
    pedido = col.find_one({"_id": ObjectId(pedido_id)})
    if not pedido:
        return jsonify({"ok": False, "msg": "Pedido no encontrado"}), 404
    
    # Buscar el pago
    pago_encontrado = None
    for i, pago in enumerate(pedido.get("pagos", [])):
        if i == int(pago_id):
            pago_encontrado = pago
            pago_index = i
            break
    
    if not pago_encontrado:
        return jsonify({"ok": False, "msg": "Pago no encontrado"}), 404
    
    # Actualizar el estado del pago
    col.update_one(
        {"_id": ObjectId(pedido_id)},
        {
            "$set": {
                f"pagos.{pago_index}.estado": "rechazado",
                f"pagos.{pago_index}.motivoRechazo": motivo or "No especificado",
                f"pagos.{pago_index}.fechaRechazo": _now_utc(),
                "updatedAt": _now_utc()
            },
            "$push": {
                "timeline": {
                    "evento": "pago_rechazado",
                    "ts": _now_utc(),
                    "nota": f"Pago de ${float(pago_encontrado['monto']):.2f} rechazado. Motivo: {motivo or 'No especificado'}"
                }
            }
        }
    )
    
    # Obtener el pedido actualizado
    pedido_actualizado = col.find_one({"_id": ObjectId(pedido_id)})
    
    return jsonify({
        "ok": True,
        "msg": "Pago rechazado",
        "pedido": _serialize(pedido_actualizado)
    }), 200

def registrar_pago(pedido_id: str, data: dict):
    """
    Registra un nuevo pago del cliente (siempre pendiente de aprobación).
    """
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

        # ✅ CALCULAR TOTALES PRIMERO (antes de usar la variable)
        totales = calcular_totales_pago(pedido)
        
        # ✅ LOGGING TEMPORAL PARA DEBUG (después de calcular totales)
        current_app.logger.info(f"=== DEBUG PAGO ===")
        current_app.logger.info(f"Monto recibido: {data['monto']} (tipo: {type(data['monto'])})")
        current_app.logger.info(f"Monto parseado: {monto}")
        current_app.logger.info(f"Saldo pendiente: {totales['saldo_pendiente']}")
        current_app.logger.info(f"Diferencia: {monto - totales['saldo_pendiente']}")
        
        # ✅ AGREGAR TOLERANCIA DE 0.02 PARA REDONDEO
        tolerancia = 0.02
        diferencia = monto - totales["saldo_pendiente"]
        
        # Si la diferencia es muy pequeña, ajustar al saldo pendiente exacto
        if 0 < diferencia <= tolerancia:
            current_app.logger.info(
                f"Ajustando monto de {monto} a {totales['saldo_pendiente']} "
                f"(diferencia: {diferencia})"
            )
            monto = float(totales["saldo_pendiente"])
        
        # Validar que no exceda significativamente
        if diferencia > tolerancia:
            return jsonify({
                "ok": False, 
                "msg": f"El monto (${monto:.2f}) excede el saldo pendiente (${totales['saldo_pendiente']:.2f})"
            }), 400

        # Crear objeto de pago (PENDIENTE de aprobación)
        nuevo_pago = {
            "monto": round(monto, 2),  # ✅ Redondear a 2 decimales
            "fecha": _now_utc(),
            "referencia": data["referencia"],
            "comprobante": data.get("imagenComprobante", ""),
            "tipo": "parcial",  # Pagos adicionales siempre son parciales
            "estado": "pendiente",  # ✅ Requiere aprobación
            "nota": data.get("nota", "Pago adicional registrado - Pendiente de aprobación")
        }

        # Actualizar el pedido
        update_data = {
            "$push": {
                "pagos": nuevo_pago,
                "timeline": {
                    "evento": "pago_registrado",
                    "ts": _now_utc(),
                    "nota": f"Nuevo pago de ${monto:.2f} registrado (Ref: {data['referencia']}) - Pendiente de aprobación"
                }
            },
            "$set": {
                "updatedAt": _now_utc()
            }
        }

        col.update_one({"_id": ObjectId(pedido_id)}, update_data)

        # Obtener el pedido actualizado
        pedido_actualizado = col.find_one({"_id": ObjectId(pedido_id)})
        
        current_app.logger.info(f"✅ Pago registrado exitosamente: ${monto:.2f}")
        
        return jsonify({
            "ok": True,
            "msg": "Pago registrado exitosamente. Esperando aprobación del administrador.",
            "pedido": _serialize(pedido_actualizado)
        })

    except (ValueError, TypeError) as e:
        current_app.logger.error(f"Error en formato de datos: {str(e)}")
        return jsonify({"ok": False, "msg": "Error en el formato de los datos"}), 400
    except Exception as e:
        current_app.logger.error(f"Error al registrar pago: {str(e)}")
        return jsonify({"ok": False, "msg": "Error al procesar el pago"}), 500


def validar_transicion_estado(pedido: dict, nuevo_estado: str) -> dict:
    """
    Valida si se puede cambiar al nuevo estado según el estado de pago.
    
    Returns:
        dict con 'valido' (bool), 'mensaje' (str) y opcionalmente 'advertencia' (str)
    """
    estado_actual = pedido["estado"]
    estado_pago = pedido.get("estadoPago", "pago_pendiente")
    totales = calcular_totales_pago(pedido)
    
    # Verificar si hay pagos pendientes
    pagos_pendientes = [p for p in pedido.get("pagos", []) if p.get("estado") == "pendiente"]
    hay_pagos_pendientes = len(pagos_pendientes) > 0
    
    # ✅ Regla 1: en_revision → en_produccion
    if estado_actual == "en_revision" and nuevo_estado == "en_produccion":
        if hay_pagos_pendientes:
            return {
                "valido": False,
                "mensaje": "⚠️ Debes aprobar o rechazar todos los comprobantes de pago pendientes antes de iniciar producción."
            }
        
        if estado_pago == "pago_pendiente":
            return {
                "valido": False,
                "mensaje": f"⚠️ Se requiere al menos el 50% del pago aprobado para iniciar producción. Actual: {totales['porcentaje_pagado']}%"
            }
        
        if estado_pago == "pago_parcial":
            return {
                "valido": True,
                "advertencia": f"⚠️ IMPORTANTE: Iniciando producción con pago parcial ({totales['porcentaje_pagado']}%). " +
                              f"Saldo pendiente: ${totales['saldo_pendiente']:.2f}"
            }
        
        return {"valido": True}
    
    # ✅ Regla 2: en_produccion → listo
    if estado_actual == "en_produccion" and nuevo_estado == "listo":
        if hay_pagos_pendientes:
            return {
                "valido": True,
                "advertencia": "⚠️ Hay comprobantes de pago pendientes de aprobación. Revísalos para actualizar el estado de pago."
            }
        
        if estado_pago != "pago_completo":
            return {
                "valido": True,
                "advertencia": f"⚠️ El pedido está listo pero el pago no está completo ({totales['porcentaje_pagado']}%). " +
                              f"Saldo pendiente: ${totales['saldo_pendiente']:.2f}"
            }
        
        return {"valido": True}
    
    # ✅ Regla 3: listo → enviado/retiro
    if estado_actual == "listo" and nuevo_estado in ["enviado", "retiro"]:
        if hay_pagos_pendientes:
            return {
                "valido": False,
                "mensaje": "❌ No se puede enviar/entregar el pedido. Hay comprobantes de pago pendientes de aprobación."
            }
        
        if estado_pago != "pago_completo":
            return {
                "valido": False,
                "mensaje": f"❌ No se puede enviar/entregar el pedido sin pago completo. " +
                          f"Pagado: {totales['porcentaje_pagado']}%, falta: ${totales['saldo_pendiente']:.2f}"
            }
        
        return {"valido": True}
    
    # ✅ Regla 4: enviado/retiro → entregado
    if estado_actual in ["enviado", "retiro"] and nuevo_estado == "entregado":
        if estado_pago != "pago_completo":
            return {
                "valido": False,
                "mensaje": "❌ No se puede marcar como entregado sin pago completo."
            }
        
        return {"valido": True}
    
    # ✅ Regla 5: Cancelación
    if nuevo_estado == "cancelado":
        return {"valido": True}
    
    # Por defecto permitir (para estados no validados explícitamente)
    return {"valido": True}

def cambiar_estado_pedido(pedido_id: str, nuevo_estado: str, nota_admin: str = None, fechaEntrega: str = None):
    """
    Cambia el estado del pedido con validaciones de pago y genera factura automáticamente.
    """
    col = get_pedidos_collection()
    pedido = col.find_one({"_id": ObjectId(pedido_id)})
    
    if not pedido:
        return jsonify({"ok": False, "msg": "Pedido no encontrado"}), 404

    from flask_api.modelo.modelo_pedido import calcular_info_pago
    infoPago = calcular_info_pago(pedido)

    col.update_one(
        {"_id": ObjectId(pedido_id)},
        {"$set": {"infoPago": infoPago}}
    )
    # Refrescar el pedido con los datos actualizados
    pedido = col.find_one({"_id": ObjectId(pedido_id)})
    
    # ✅ VALIDACIÓN ESPECIAL: No se puede cambiar a "listo" sin pago completo
    if nuevo_estado == "listo":
        infoPago = pedido.get("infoPago", {})
        estado_pago = infoPago.get("estado_pago", "")
        
        if estado_pago != "pago_completo":
            porcentaje = infoPago.get("porcentaje_pagado", 0)
            saldo = infoPago.get("saldo_pendiente", 0)
            
            return jsonify({
                "ok": False,
                "msg": f"❌ No se puede marcar como 'Listo'. El pago no está completo.\n\n"
                       f"📊 Estado actual: {porcentaje}% pagado\n"
                       f"💰 Saldo pendiente: ${saldo:.2f}\n\n"
                       f"Por favor, espera a que el cliente complete el pago al 100%."
            }), 400
    
    # Validar transición
    validacion = validar_transicion_estado(pedido, nuevo_estado)
    
    if not validacion["valido"]:
        return jsonify({"ok": False, "msg": validacion["mensaje"]}), 400
    
    # ✅ GENERAR FACTURA AUTOMÁTICAMENTE al pasar a "listo"
    factura_url = None
    if pedido["estado"] == "en_produccion" and nuevo_estado == "listo":
        infoPago = pedido.get("infoPago", {})
        if infoPago.get("estado_pago") == "pago_completo":
            from flask_api.controlador.control_factura import generar_factura_pdf
            
            current_app.logger.info(f"📄 Generando factura para pedido {pedido_id}")
            success, resultado = generar_factura_pdf(pedido_id)
            
            if success:
                factura_url = resultado
                current_app.logger.info(f"✅ Factura generada: {factura_url}")
            else:
                current_app.logger.warning(f"⚠️ No se pudo generar factura: {resultado}")
                # No fallar el cambio de estado, solo advertir
    
    try:
        ok = update_pedido_status(pedido_id, nuevo_estado, nota_admin, fechaEntrega)
    except ValueError as e:
        return jsonify({"ok": False, "msg": str(e)}), 400

    if not ok:
        return jsonify({"ok": False, "msg": "Error al actualizar estado"}), 404

    # ✅ Si se generó factura, guardarla en el pedido
    if factura_url:
        col.update_one(
            {"_id": ObjectId(pedido_id)},
            {
                "$set": {
                    "facturaUrl": factura_url,
                    "facturaGenerada": _now_utc()
                }
            }
        )

    response = {"ok": True, "msg": "Estado actualizado correctamente"}
    
    # Incluir advertencia si existe
    if validacion.get("advertencia"):
        response["advertencia"] = validacion["advertencia"]
    
    # ✅ Incluir URL de factura si se generó
    if factura_url:
        response["facturaUrl"] = factura_url
        response["msg"] += " ✅ Factura generada exitosamente."
    
    return jsonify(response), 200


def confirmar_pedido_transferencia(usuario_id: str, data: dict, imagen_url: str):
    """
    Confirma un pedido con transferencia bancaria.
    El pago queda en estado pendiente hasta que el admin lo apruebe.
    """
    try:
        col = get_pedidos_collection()
        
        # Parsear los datos del pedido
        pedido_data = data
        
        # Validar campos requeridos
        required_fields = ['items', 'direccionEnvio', 'metodoPago', 'costos', 'referenciaPago']
        for field in required_fields:
            if field not in pedido_data:
                return jsonify({"ok": False, "msg": f"Falta el campo requerido: {field}"}), 400
        
        # Obtener datos
        items = pedido_data['items']
        direccion_envio = pedido_data['direccionEnvio']
        metodo_pago = pedido_data['metodoPago']
        tipo_pago = pedido_data.get('tipoPago', 'completo')
        tipo_entrega = pedido_data.get('tipoEntrega', 'domicilio')  # ✅ IMPORTANTE
        referencia_pago = pedido_data['referenciaPago']
        costos = pedido_data['costos']
        monto_pago = pedido_data.get('montoPago', costos['total'])
        
        # Validar que haya items
        if not items or len(items) == 0:
            return jsonify({"ok": False, "msg": "El pedido debe tener al menos un producto"}), 400

        # Obtener información del usuario
        usuario_col = get_users_collection()
        usuario = usuario_col.find_one({"_id": ObjectId(usuario_id)})
        
        if not usuario:
            return jsonify({"ok": False, "msg": "Usuario no encontrado"}), 404
        
        # ✅ Preparar el pago inicial (siempre pendiente de aprobación)
        pago_inicial = {
            "monto": float(monto_pago),
            "fecha": _now_utc(),
            "referencia": referencia_pago,
            "comprobante": imagen_url,
            "tipo": "anticipo" if tipo_pago == "anticipo" else "completo",
            "estado": "pendiente",  # ✅ Siempre pendiente hasta que admin apruebe
            "nota": f"Pago {'parcial (50%)' if tipo_pago == 'anticipo' else 'completo'} - Transferencia bancaria - Pendiente de aprobación"
        }
        
        # ✅ Calcular información de pago
        total_pedido = float(costos['total'])
        total_pagado = 0  # Aún no se ha aprobado ningún pago
        saldo_pendiente = total_pedido
        porcentaje_pagado = 0
        
        # ✅ El estado de pago inicial es siempre pendiente
        estado_pago_inicial = "pago_pendiente"
        
        # ✅ Construir el documento del pedido
        nuevo_pedido = {
            "userId": ObjectId(usuario_id),
            "clienteNombre": f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}".strip(),
            "clienteCorreo": usuario.get('correo', ''),
            "items": items,
            "direccionEnvio": direccion_envio,
            "metodoPago": metodo_pago,
            "tipoPago": tipo_pago,
            "tipoEntrega": tipo_entrega,  # ✅ Guardar tipo de entrega
            "costos": {
                "subtotal": float(costos['subtotal']),
                "envio": float(costos['envio']),
                "impuestos": float(costos['impuestos']),
                "total": total_pedido
            },
            "pagos": [pago_inicial],
            "infoPago": {
                "total_pedido": total_pedido,
                "total_pagado": total_pagado,
                "saldo_pendiente": saldo_pendiente,
                "porcentaje_pagado": porcentaje_pagado,
                "estado_pago": estado_pago_inicial
            },
            "estado": "en_revision",  # ✅ Estado inicial: en revisión
            "timeline": [
                {
                    "evento": "pedido_creado",
                    "ts": _now_utc(),
                    "nota": f"Pedido creado con pago {'parcial (50%)' if tipo_pago == 'anticipo' else 'completo'} pendiente de aprobación"
                }
            ],
            "createdAt": _now_utc(),
            "updatedAt": _now_utc()
        }
        
        # Insertar el pedido en la base de datos
        result = col.insert_one(nuevo_pedido)
        
        if not result.inserted_id:
            return jsonify({"ok": False, "msg": "Error al crear el pedido"}), 500
        
        # Obtener el pedido insertado
        pedido_insertado = col.find_one({"_id": result.inserted_id})
        
        current_app.logger.info(f"Pedido creado exitosamente: {result.inserted_id}")
        
        return jsonify({
            "ok": True,
            "msg": "Pedido creado exitosamente. Tu pago será revisado en las próximas 24-48 horas.",
            "pedido": _serialize(pedido_insertado),
            "pedidoId": str(result.inserted_id)
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error al confirmar pedido: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"ok": False, "msg": f"Error al procesar el pedido: {str(e)}"}), 500



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

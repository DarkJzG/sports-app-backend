from flask import jsonify, current_app
import io
import cloudinary
import logging
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
from flask_api.controlador.control_ficha_tecnica import construir_ficha_tecnica_detallada
from flask_api.controlador.control_pedido_ficha import generar_ficha_tecnica_pedido
from flask_api.controlador.control_proforma import generar_pdf_proforma
from flask_api.modelo.modelo_ficha_tecnica import guardar_ficha, get_fichas_collection
from flask_api.modelo.modelo_3d_prenda import get_prendas3d_collection

log = logging.getLogger(__name__)

FICHA_URL_KEYS = [
    "ficha_pdf_url",
    "ficha_tecnica_url",
    "ficha_tecnica_pdf",
    "fichaPdfUrl",
    "url_pdf",
    "pdf_url",
]

def _extraer_ficha_url(*docs):
    """
    Intenta encontrar una URL de ficha técnica en uno o varios documentos
    (diseño IA, prenda 3D, etc.) usando una lista de posibles nombres de campo.
    """
    for doc in docs:
        if not doc:
            continue
        for k in FICHA_URL_KEYS:
            val = doc.get(k)
            if val:
                return val
    return None


def _build_item_pedido_desde_carrito(item_carrito, diseno_ia=None, prenda_3d=None):
    """
    Construye la estructura del item que se guardará en el pedido a partir del item del carrito
    y la info de la prenda IA / 3D. Unifica el campo ficha_pdf_url.
    """
    cantidad = int(item_carrito.get("cantidad", 1) or 1)
    precio_unit = float(
        item_carrito.get("precioUnitario")
        or item_carrito.get("precio_unitario")
        or item_carrito.get("precio")
        or 0
    )

    base = {
        "producto_id": str(item_carrito.get("producto_id") or ""),
        "tipo": item_carrito.get("tipo") or "normal",  # ia / 3d / etc.
        "nombre": item_carrito.get("nombre")
                  or (diseno_ia or {}).get("nombre")
                  or (prenda_3d or {}).get("modelo")
                  or "Producto",
        "talla": item_carrito.get("talla") or "N/A",
        "cantidad": cantidad,
        "precioUnitario": precio_unit,
        "precioTotal": float(item_carrito.get("precioTotal") or precio_unit * cantidad),
        "imagen": item_carrito.get("imagen")
                  or (diseno_ia or {}).get("imagen")
                  or (prenda_3d or {}).get("renders", {}).get("render_frente"),
    }

    # IDs de ficha (para IA o 3D)
    if diseno_ia and diseno_ia.get("_id"):
        base["ficha_id"] = str(diseno_ia.get("ficha_id") or diseno_ia["_id"])
    if prenda_3d and prenda_3d.get("_id"):
        base["prenda3d_id"] = str(prenda_3d["_id"])

    # 🔗 URL unificada de ficha técnica
    ficha_url = _extraer_ficha_url(diseno_ia, prenda_3d, item_carrito)
    if ficha_url:
        base["ficha_pdf_url"] = ficha_url
        log.info(
            "📎 Ficha técnica asociada al item %s: %s",
            base["nombre"],
            ficha_url,
        )

    return base

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
                "nota": (
                    f"Pago de ${float(pago_encontrado['monto']):.2f} aprobado. "
                    f"Total pagado: ${totales['total_pagado']:.2f} de ${totales['total_pedido']:.2f} "
                    f"({totales['porcentaje_pagado']}%)"
                )
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
                    "nota": (
                        f"Pago de ${float(pago_encontrado['monto']):.2f} rechazado. "
                        f"Motivo: {motivo or 'No especificado'}"
                    )
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

        # ✅ CALCULAR TOTALES PRIMERO
        totales = calcular_totales_pago(pedido)
        
        current_app.logger.info("=== DEBUG PAGO ===")
        current_app.logger.info(f"Monto recibido: {data['monto']} (tipo: {type(data['monto'])})")
        current_app.logger.info(f"Monto parseado: {monto}")
        current_app.logger.info(f"Saldo pendiente: {totales['saldo_pendiente']}")
        current_app.logger.info(f"Diferencia: {monto - totales['saldo_pendiente']}")

        tolerancia = 0.02
        diferencia = monto - totales["saldo_pendiente"]
        
        if 0 < diferencia <= tolerancia:
            current_app.logger.info(
                f"Ajustando monto de {monto} a {totales['saldo_pendiente']} "
                f"(diferencia: {diferencia})"
            )
            monto = float(totales["saldo_pendiente"])
        
        if diferencia > tolerancia:
            return jsonify({
                "ok": False,
                "msg": (
                    f"El monto (${monto:.2f}) excede el saldo pendiente "
                    f"(${totales['saldo_pendiente']:.2f})"
                )
            }), 400

        nuevo_pago = {
            "monto": round(monto, 2),
            "fecha": _now_utc(),
            "referencia": data["referencia"],
            "comprobante": data.get("imagenComprobante", ""),
            "tipo": "parcial",
            "estado": "pendiente",
            "nota": data.get(
                "nota",
                "Pago adicional registrado - Pendiente de aprobación"
            )
        }

        update_data = {
            "$push": {
                "pagos": nuevo_pago,
                "timeline": {
                    "evento": "pago_registrado",
                    "ts": _now_utc(),
                    "nota": (
                        f"Nuevo pago de ${monto:.2f} registrado "
                        f"(Ref: {data['referencia']}) - Pendiente de aprobación"
                    )
                }
            },
            "$set": {"updatedAt": _now_utc()}
        }

        col.update_one({"_id": ObjectId(pedido_id)}, update_data)

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
    
    pagos_pendientes = [p for p in pedido.get("pagos", []) if p.get("estado") == "pendiente"]
    hay_pagos_pendientes = len(pagos_pendientes) > 0
    
    if estado_actual == "en_revision" and nuevo_estado == "en_produccion":
        if hay_pagos_pendientes:
            return {
                "valido": False,
                "mensaje": (
                    "⚠️ Debes aprobar o rechazar todos los comprobantes de pago "
                    "pendientes antes de iniciar producción."
                )
            }
        
        if estado_pago == "pago_pendiente":
            return {
                "valido": False,
                "mensaje": (
                    "⚠️ Se requiere al menos el 50% del pago aprobado para "
                    f"iniciar producción. Actual: {totales['porcentaje_pagado']}%"
                )
            }
        
        if estado_pago == "pago_parcial":
            return {
                "valido": True,
                "advertencia": (
                    "⚠️ IMPORTANTE: Iniciando producción con pago parcial "
                    f"({totales['porcentaje_pagado']}%). "
                    f"Saldo pendiente: ${totales['saldo_pendiente']:.2f}"
                )
            }
        
        return {"valido": True}
    
    if estado_actual == "en_produccion" and nuevo_estado == "listo":
        if hay_pagos_pendientes:
            return {
                "valido": True,
                "advertencia": (
                    "⚠️ Hay comprobantes de pago pendientes de aprobación. "
                    "Revísalos para actualizar el estado de pago."
                )
            }
        
        if estado_pago != "pago_completo":
            return {
                "valido": True,
                "advertencia": (
                    "⚠️ El pedido está listo pero el pago no está completo "
                    f"({totales['porcentaje_pagado']}%). "
                    f"Saldo pendiente: ${totales['saldo_pendiente']:.2f}"
                )
            }
        
        return {"valido": True}
    
    if estado_actual == "listo" and nuevo_estado in ["enviado", "retiro"]:
        if hay_pagos_pendientes:
            return {
                "valido": False,
                "mensaje": (
                    "❌ No se puede enviar/entregar el pedido. Hay comprobantes "
                    "de pago pendientes de aprobación."
                )
            }
        
        if estado_pago != "pago_completo":
            return {
                "valido": False,
                "mensaje": (
                    "❌ No se puede enviar/entregar el pedido sin pago completo. "
                    f"Pagado: {totales['porcentaje_pagado']}%, "
                    f"falta: ${totales['saldo_pendiente']:.2f}"
                )
            }
        
        return {"valido": True}
    
    if estado_actual in ["enviado", "retiro"] and nuevo_estado == "entregado":
        if estado_pago != "pago_completo":
            return {
                "valido": False,
                "mensaje": "❌ No se puede marcar como entregado sin pago completo."
            }
        
        return {"valido": True}
    
    if nuevo_estado == "cancelado":
        return {"valido": True}
    
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
    pedido = col.find_one({"_id": ObjectId(pedido_id)})
    
    if nuevo_estado == "listo":
        infoPago = pedido.get("infoPago", {})
        estado_pago = infoPago.get("estado_pago", "")
        
        if estado_pago != "pago_completo":
            porcentaje = infoPago.get("porcentaje_pagado", 0)
            saldo = infoPago.get("saldo_pendiente", 0)
            
            return jsonify({
                "ok": False,
                "msg": (
                    "❌ No se puede marcar como 'Listo'. El pago no está completo.\n\n"
                    f"📊 Estado actual: {porcentaje}% pagado\n"
                    f"💰 Saldo pendiente: ${saldo:.2f}\n\n"
                    "Por favor, espera a que el cliente complete el pago al 100%."
                )
            }), 400
    
    validacion = validar_transicion_estado(pedido, nuevo_estado)
    
    if not validacion["valido"]:
        return jsonify({"ok": False, "msg": validacion["mensaje"]}), 400
    
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

    try:
        ok = update_pedido_status(pedido_id, nuevo_estado, nota_admin, fechaEntrega)
    except ValueError as e:
        return jsonify({"ok": False, "msg": str(e)}), 400

    if not ok:
        return jsonify({"ok": False, "msg": "Error al actualizar estado"}), 404

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
    
    if validacion.get("advertencia"):
        response["advertencia"] = validacion["advertencia"]
    
    if factura_url:
        response["facturaUrl"] = factura_url
        response["msg"] += " ✅ Factura generada exitosamente."
    
    return jsonify(response), 200

def confirmar_pedido_transferencia(usuario_id: str, data: dict, imagen_url: str):
    """
    Confirma un pedido con transferencia bancaria.
    El pago queda en estado pendiente hasta que el admin lo apruebe.
    Además:
    - Genera fichas técnicas por ítem IA/3D si no existen.
    - Genera ficha técnica consolidada del pedido.
    - Genera PDF de PROFORMA con detalle de productos, tallas, cantidades,
      totales y enlace a ficha técnica (si la hay).
    """
    try:
        col = get_pedidos_collection()
        
        pedido_data = data
        
        required_fields = ['items', 'direccionEnvio', 'metodoPago', 'costos', 'referenciaPago']
        for field in required_fields:
            if field not in pedido_data:
                return jsonify({"ok": False, "msg": f"Falta el campo requerido: {field}"}), 400
        
        items = pedido_data['items']
        direccion_envio = pedido_data['direccionEnvio']
        metodo_pago = pedido_data['metodoPago']
        tipo_pago = pedido_data.get('tipoPago', 'completo')
        tipo_entrega = pedido_data.get('tipoEntrega', 'domicilio')
        referencia_pago = pedido_data['referenciaPago']
        costos = pedido_data['costos']
        monto_pago = pedido_data.get('montoPago', costos['total'])
        
        if not items or len(items) == 0:
            return jsonify({"ok": False, "msg": "El pedido debe tener al menos un producto"}), 400

        usuario_col = get_users_collection()
        usuario = usuario_col.find_one({"_id": ObjectId(usuario_id)})
        
        if not usuario:
            return jsonify({"ok": False, "msg": "Usuario no encontrado"}), 404
        
        # ✅ ENRIQUECER ITEMS CON FICHAS TÉCNICAS (IA / 3D, etc.)
        items_con_ficha = []
        for item in items:
            tipo_item = item.get("tipo")

            # Solo generamos ficha si aún no tiene ficha_id
            if tipo_item in ["ia_prenda", "prenda3d"] and not item.get("ficha_id"):
                atributos = item.get("atributos_es") or item.get("atributos") or {}
                categoria = (
                    item.get("categoria_prd")
                    or atributos.get("categoria_prd")
                    or "prenda"
                )

                image_urls = {
                    "delantera": item.get("imagen_frente") or item.get("imagen"),
                    "posterior": item.get("imagen_espalda"),
                    "acabado": item.get("imagen") or item.get("imagen_acabado"),
                }

                ficha = construir_ficha_tecnica_detallada(
                    categoria_prd=categoria,
                    atributos=atributos,
                    image_urls=image_urls
                )

                if item.get("costo"):
                    ficha["costo"] = item["costo"]
                if item.get("talla"):
                    ficha["talla"] = item["talla"]

                ficha_doc = {
                    "user_id": usuario_id,
                    "prenda_id": item.get("productId") or item.get("prenda3d_id"),
                    "pedido_preview": {
                        "nombre": item.get("nombre"),
                        "talla": item.get("talla"),
                        "cantidad": item.get("cantidad"),
                    },
                    "ficha": ficha,
                }

                try:
                    ficha_id = guardar_ficha(ficha_doc)
                    item["ficha_id"] = ficha_id
                    current_app.logger.info(
                        f"🧾 Ficha técnica guardada para item con productId={item.get('productId')}, ficha_id={ficha_id}"
                    )
                except Exception as e:
                    current_app.logger.warning(
                        f"⚠️ No se pudo guardar ficha técnica para item {item.get('productId')}: {e}"
                    )

            items_con_ficha.append(item)

        items = items_con_ficha

        # 🧾 Pago inicial registrado como pendiente
        pago_inicial = {
            "monto": float(monto_pago),
            "fecha": _now_utc(),
            "referencia": referencia_pago,
            "comprobante": imagen_url,
            "tipo": "anticipo" if tipo_pago == "anticipo" else "completo",
            "estado": "pendiente",
            "nota": (
                f"Pago {'parcial (50%)' if tipo_pago == 'anticipo' else 'completo'} "
                " - Transferencia bancaria - Pendiente de aprobación"
            )
        }
        
        total_pedido = float(costos['total'])
        total_pagado = 0
        saldo_pendiente = total_pedido
        porcentaje_pagado = 0
        estado_pago_inicial = "pago_pendiente"
        
        nuevo_pedido = {
            "userId": ObjectId(usuario_id),
            "clienteNombre": f"{usuario.get('nombre', '')} {usuario.get('apellido', '')}".strip(),
            "clienteCorreo": usuario.get('correo', ''),
            "items": items,
            "direccionEnvio": direccion_envio,
            "metodoPago": metodo_pago,
            "tipoPago": tipo_pago,
            "tipoEntrega": tipo_entrega,
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
            "estado": "en_revision",
            "timeline": [
                {
                    "evento": "pedido_creado",
                    "ts": _now_utc(),
                    "nota": (
                        "Pedido creado con pago "
                        f"{'parcial (50%)' if tipo_pago == 'anticipo' else 'completo'} "
                        "pendiente de aprobación"
                    )
                }
            ],
            "createdAt": _now_utc(),
            "updatedAt": _now_utc()
        }

        result = col.insert_one(nuevo_pedido)
        
        if not result.inserted_id:
            return jsonify({"ok": False, "msg": "Error al crear el pedido"}), 500

        pedido_oid = result.inserted_id
        pedido_id = str(pedido_oid)

        # 📥 Recargar pedido desde BD (ya con todo lo que se guardó)
        pedido_insertado = col.find_one({"_id": pedido_oid})

        # ✅ Generar PROFORMA PDF
        proforma_url = None
        try:
            fichas_col = get_fichas_collection()
            prendas3d_col = None  # la cargamos solo si hace falta
            items_pdf = []

            for it in pedido_insertado.get("items", []):
                it_copy = dict(it)

                ficha_doc = None
                ficha_url = None

                # 0️⃣ Si el ítem YA trae una URL directa, la respetamos
                ficha_url = _extraer_ficha_url(it_copy)

                # 1️⃣ Si tiene ficha_id, buscamos en la colección genérica de fichas
                if not ficha_url:
                    ficha_id = it_copy.get("ficha_id")
                    if ficha_id:
                        try:
                            ficha_doc = fichas_col.find_one({"_id": ObjectId(ficha_id)})
                        except Exception as e:
                            current_app.logger.warning(
                                f"⚠️ Error buscando ficha por _id={ficha_id}: {e}"
                            )

                # 2️⃣ Si no hay ficha_doc todavía, buscamos por prenda_id en fichas genéricas
                if not ficha_url and not ficha_doc:
                    prenda_id = (
                        it_copy.get("productId")
                        or it_copy.get("prenda3d_id")
                        or it_copy.get("prenda_id")
                    )
                    if prenda_id:
                        try:
                            ficha_doc = fichas_col.find_one({"prenda_id": prenda_id})
                        except Exception as e:
                            current_app.logger.warning(
                                f"⚠️ Error buscando ficha por prenda_id={prenda_id}: {e}"
                            )

                # 3️⃣ Si tenemos ficha_doc, intentamos extraer URL de ahí
                if not ficha_url and ficha_doc:
                    ficha_url = _extraer_ficha_url(ficha_doc)

                # 4️⃣ Si sigue sin URL, intentamos buscar en prendas_3d por id o modelo
                if not ficha_url:
                    try:
                        if prendas3d_col is None:
                            prendas3d_col = get_prendas3d_collection()

                        prenda3d_doc = None

                        # Candidatos posibles de identificador / modelo
                        candidatos = []

                        for key in ["productId", "prenda3d_id", "productoId", "modelo", "codigo", "sku"]:
                            val = it_copy.get(key)
                            if val:
                                candidatos.append(val)

                        # A veces el nombre ES el modelo: "CH-1765..." / "PT-..."
                        nombre_item = it_copy.get("nombre")
                        if isinstance(nombre_item, str) and "-" in nombre_item and len(nombre_item) <= 40:
                            candidatos.append(nombre_item)

                        for cand in candidatos:
                            # Intentar como ObjectId
                            try:
                                prenda3d_doc = prendas3d_col.find_one({"_id": ObjectId(cand)})
                            except Exception:
                                # Si no es ObjectId, probamos como modelo
                                prenda3d_doc = prendas3d_col.find_one({"modelo": cand})

                            if prenda3d_doc:
                                break

                        if prenda3d_doc:
                            ficha_url = _extraer_ficha_url(prenda3d_doc)

                    except Exception as e:
                        current_app.logger.warning(
                            f"⚠️ Error buscando ficha 3D para item {it_copy.get('nombre')}: {e}"
                        )

                # 5️⃣ Guardar URL (o None) en el ítem para la columna "Ficha técnica"
                it_copy["ficha_pdf_url"] = ficha_url or None
                items_pdf.append(it_copy)

            # Construir pedido para el PDF
            pedido_para_pdf = dict(pedido_insertado)
            pedido_para_pdf["items"] = items_pdf

            empresa_doc = current_app.config.get("EMPRESA_DOC", {}) or {}
            usuario_pdf = {
                "nombre_completo": pedido_para_pdf.get("clienteNombre", ""),
                "email": pedido_para_pdf.get("clienteCorreo", "")
            }

            pdf_bytes = generar_pdf_proforma(
                pedido_para_pdf,
                empresa_doc,
                usuario_pdf
            )

            pdf_io = io.BytesIO(pdf_bytes)
            upload = cloudinary.uploader.upload(
                pdf_io,
                folder="proformas",
                public_id=f"proforma_{pedido_id}",
                resource_type="raw",
                format="pdf"
            )
            proforma_url = upload.get("secure_url")

            if proforma_url:
                col.update_one(
                    {"_id": pedido_oid},
                    {"$set": {"proformaUrl": proforma_url}}
                )
                current_app.logger.info(f"📄 Proforma generada para pedido {pedido_id}: {proforma_url}")

        except Exception as e:
            current_app.logger.warning(
                f"⚠️ No se pudo generar/subir proforma para pedido {pedido_id}: {e}"
            )

        current_app.logger.info(f"Pedido creado exitosamente: {pedido_oid}")
        
        pedido_insertado = col.find_one({"_id": pedido_oid})

        return jsonify({
            "ok": True,
            "msg": "Pedido creado exitosamente. Tu pago será revisado en las próximas 24-48 horas.",
            "pedido": _serialize(pedido_insertado),
            "pedidoId": pedido_id,
            "proformaUrl": proforma_url    # 👈 la proforma queda disponible para el frontend
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

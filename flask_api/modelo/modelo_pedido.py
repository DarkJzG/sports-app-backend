# flask_api/modelo/modelo_pedido.py
from flask import current_app
from bson import ObjectId
from datetime import datetime, timezone

# Estados de pago (calculados automáticamente según pagos aprobados)
ESTADOS_PAGO = [
    "pago_pendiente",   # < 50% pagado
    "pago_parcial",     # >= 50% y < 100% pagado
    "pago_completo"     # 100% pagado
]

# Estados del pedido (flujo de producción/logística)
ESTADOS_PEDIDO = [
    "en_revision",      # Recién creado, esperando aprobación de pagos
    "en_produccion",    # Fabricando/preparando
    "listo",            # Terminado, listo para envío
    "enviado",          # En camino al cliente
    "retiro",           # Esperando retiro en tienda
    "entregado",        # Completado exitosamente
    "cancelado"         # Cancelado
]


def get_pedidos_collection():
    return current_app.mongo.db.pedidos


def _now_utc():
    return datetime.now(timezone.utc)


def calcular_estado_pago(pedido: dict) -> str:
    """
    Calcula el estado de pago basándose en los pagos aprobados.
    
    Returns:
        - "pago_pendiente": < 50% pagado
        - "pago_parcial": >= 50% y < 100% pagado
        - "pago_completo": 100% pagado
    """
    total_pedido = float(pedido["costos"]["total"])
    
    # Sumar solo pagos aprobados
    pagos_aprobados = [p for p in pedido.get("pagos", []) if p.get("estado") == "aprobado"]
    total_pagado = sum(float(p.get("monto", 0)) for p in pagos_aprobados)
    
    porcentaje = (total_pagado / total_pedido) * 100 if total_pedido > 0 else 0
    
    if porcentaje >= 100:
        return "pago_completo"
    elif porcentaje >= 50:
        return "pago_parcial"
    else:
        return "pago_pendiente"


def calcular_totales_pago(pedido: dict) -> dict:
    """
    Calcula información detallada sobre el estado de pago.
    """
    total_pedido = float(pedido["costos"]["total"])
    
    pagos_aprobados = [p for p in pedido.get("pagos", []) if p.get("estado") == "aprobado"]
    total_pagado = sum(float(p.get("monto", 0)) for p in pagos_aprobados)
    saldo_pendiente = max(total_pedido - total_pagado, 0)
    porcentaje = (total_pagado / total_pedido) * 100 if total_pedido > 0 else 0
    
    return {
        "total_pedido": total_pedido,
        "total_pagado": total_pagado,
        "saldo_pendiente": saldo_pendiente,
        "porcentaje_pagado": round(porcentaje, 2),
        "estado_pago": calcular_estado_pago(pedido)
    }

def calcular_info_pago(pedido: dict) -> dict:
    """
    Calcula la información consolidada de pago de un pedido.
    Retorna el mismo formato que calcular_totales_pago pero como dict independiente.
    """
    try:
        total_pedido = float(pedido.get("costos", {}).get("total", 0))
        
        if total_pedido == 0:
            return {
                "total_pedido": 0,
                "total_pagado": 0,
                "saldo_pendiente": 0,
                "porcentaje_pagado": 0,
                "estado_pago": "sin_pago"
            }
        
        # Filtrar pagos aprobados
        pagos = pedido.get("pagos", [])
        pagos_aprobados = [p for p in pagos if p.get("estado") == "aprobado"]
        
        # Calcular total pagado
        total_pagado = sum(float(p.get("monto", 0)) for p in pagos_aprobados)
        
        # Calcular saldo pendiente
        saldo_pendiente = max(0, total_pedido - total_pagado)
        
        # Calcular porcentaje pagado
        porcentaje_pagado = (total_pagado / total_pedido * 100) if total_pedido > 0 else 0
        
        # Determinar estado de pago
        if porcentaje_pagado >= 100:
            estado_pago = "pago_completo"
        elif porcentaje_pagado >= 50:
            estado_pago = "pago_parcial"
        elif porcentaje_pagado > 0:
            estado_pago = "pago_parcial"
        else:
            estado_pago = "pago_pendiente"
        
        return {
            "total_pedido": round(total_pedido, 2),
            "total_pagado": round(total_pagado, 2),
            "saldo_pendiente": round(saldo_pendiente, 2),
            "porcentaje_pagado": round(porcentaje_pagado, 2),
            "estado_pago": estado_pago
        }
        
    except Exception as e:
        current_app.logger.error(f"Error al calcular info de pago: {str(e)}")
        return {
            "total_pedido": 0,
            "total_pagado": 0,
            "saldo_pendiente": 0,
            "porcentaje_pagado": 0,
            "estado_pago": "error"
        }


def build_pedido_doc(user_id: str, data: dict) -> dict:
    """
    Construye el documento del pedido.
    Todos los pedidos inician en estado 'en_revision' con pagos pendientes de aprobación.
    """
    tipo_pago = data.get("tipoPago", "completo")
    total = float(data["costos"]["total"])

    # Calcular monto del primer pago
    if tipo_pago == "anticipo":
        monto_primer_pago = round(total * 0.5, 2)  # 50% de anticipo
    else:
        monto_primer_pago = total

    direccion = data["direccionEnvio"]
    tipo_envio = direccion.get("tipoEnvio", "domicilio")

    # Construir el documento del pedido
    pedido_doc = {
        "userId": ObjectId(user_id),
        "items": [
            {
                "productId": ObjectId(item["productId"]),
                "tipo": item.get("tipo", "producto"),
                "nombre": item["nombre"],
                "cantidad": int(item["cantidad"]),
                "precioUnitario": float(item["precioUnitario"]),
                "talla": item.get("talla"),
                "color": item.get("color"),
                "imagen": item.get("imagen") or item.get("imagen_url"),
                "ficha_id": str(item.get("ficha_id")) if item.get("ficha_id") else None
            } for item in data["items"]
        ],
        "direccionEnvio": {
            "tipoEnvio": tipo_envio,
            "nombre": direccion.get("nombre"),
            "direccion_principal": direccion.get("direccion_principal"),
            "direccion_secundaria": direccion.get("direccion_secundaria", ""),
            "ciudad": direccion.get("ciudad"),
            "provincia": direccion.get("provincia"),
            "pais": direccion.get("pais", "Ecuador"),
            "telefono": direccion.get("telefono"),
            "codigo_postal": direccion.get("codigo_postal"),
            "detalle": direccion.get("detalle", "Retiro en Tienda" if tipo_envio == "retiro" else "")
        },
        "metodoPago": data.get("metodoPago", "transferencia"),
        "tipoPago": tipo_pago,
        "costos": {
            "subtotal": float(data["costos"]["subtotal"]),
            "envio": float(data["costos"]["envio"]),
            "impuestos": float(data["costos"]["impuestos"]),
            "total": float(data["costos"]["total"]),
        },
        
        # Estados separados
        "estado": "en_revision",  # ✅ Estado del pedido (producción/logística)
        "estadoPago": "pago_pendiente",  # ✅ Estado de pago (calculado)
        
        "pagos": [],  # Historial de pagos
        "createdAt": _now_utc(),
        "updatedAt": _now_utc(),
        "timeline": [
            {
                "evento": "pedido_creado",
                "estado": "en_revision",
                "ts": _now_utc(),
                "nota": f"Pedido creado con tipo de pago: {tipo_pago}"
            }
        ],
    }

    # Si hay un comprobante de transferencia, agregarlo como primer pago PENDIENTE
    if "imagenTransferencia" in data:
        pago = {
            "monto": monto_primer_pago,
            "fecha": _now_utc(),
            "referencia": data.get("referenciaPago", "Pago inicial"),
            "comprobante": data["imagenTransferencia"],
            "tipo": "anticipo" if tipo_pago == "anticipo" else "completo",
            "estado": "pendiente",  # ✅ Requiere aprobación manual
            "nota": "Pago inicial del pedido - Pendiente de aprobación"
        }
        pedido_doc["pagos"].append(pago)
        pedido_doc["referenciaPago"] = pago["referencia"]
        pedido_doc["comprobanteTransferencia"] = pago["comprobante"]

    return pedido_doc


def insert_pedido(pedido_doc: dict):
    col = get_pedidos_collection()
    res = col.insert_one(pedido_doc)
    return str(res.inserted_id)


def find_pedidos_by_user(user_id: str, page: int = 1, limit: int = 20):
    col = get_pedidos_collection()
    skip = (page - 1) * limit
    cursor = col.find({"userId": ObjectId(user_id)}).sort("createdAt", -1).skip(skip).limit(limit)
    items = list(cursor)
    total = col.count_documents({"userId": ObjectId(user_id)})
    return _serialize_list(items), total


def find_all_pedidos(filt: dict, page: int = 1, limit: int = 20):
    col = get_pedidos_collection()
    skip = (page - 1) * limit

    pipeline = [
        {"$match": filt},
        {"$sort": {"createdAt": -1}},
        {"$skip": skip},
        {"$limit": limit},
        {"$lookup": {
            "from": "users",
            "localField": "userId",
            "foreignField": "_id",
            "as": "usuario"
        }},
        {"$unwind": {"path": "$usuario", "preserveNullAndEmptyArrays": True}},
        {"$addFields": {
            "clienteNombre": {
                "$concat": [
                    {"$ifNull": ["$usuario.nombre", ""]},
                    " ",
                    {"$ifNull": ["$usuario.apellido", ""]}
                ]
            },
            "clienteCorreo": "$usuario.correo"
        }},
        {"$project": {
            "usuario.password": 0,
        }}
    ]

    cursor = col.aggregate(pipeline)
    items = list(cursor)
    total = col.count_documents(filt)
    return _serialize_list(items), total


def update_pedido_status(pedido_id: str, nuevo_estado: str, nota_admin: str = None, fechaEntrega=None):
    """
    Actualiza el estado del pedido (producción/logística).
    """
    if nuevo_estado not in ESTADOS_PEDIDO:
        raise ValueError(f"Estado inválido: {nuevo_estado}")

    col = get_pedidos_collection()
    upd = {
        "$set": {
            "estado": nuevo_estado,
            "updatedAt": _now_utc()
        },
        "$push": {
            "timeline": {
                "evento": "cambio_estado_pedido",
                "estado": nuevo_estado,
                "nota": nota_admin,
                "ts": _now_utc()
            }
        }
    }

    if fechaEntrega:
        upd["$set"]["fechaEntrega"] = fechaEntrega

    res = col.update_one({"_id": ObjectId(pedido_id)}, upd)
    return res.modified_count == 1


def _to_iso(dt):
    try:
        return dt.isoformat().replace("+00:00", "Z")
    except Exception:
        return dt


def _serialize(doc: dict) -> dict:
    if not doc:
        return None
    
    # Serializar _id
    doc["_id"] = str(doc["_id"])
    
    # ✅ CORRECCIÓN: Manejar múltiples nombres de campo para userId
    # Buscar el campo de usuario (puede ser userId, usuarioId, user_id, etc.)
    user_id_field = None
    for field_name in ["userId", "usuarioId", "user_id"]:
        if field_name in doc:
            user_id_field = field_name
            break
    
    if user_id_field:
        # Normalizar a userId
        doc["userId"] = str(doc[user_id_field])
        # Si era otro nombre, eliminar el campo original
        if user_id_field != "userId":
            del doc[user_id_field]
    else:
        # Si no existe ningún campo de usuario, crear uno vacío
        doc["userId"] = None

    # Normalizar fechas principales
    if "createdAt" in doc:
        doc["createdAt"] = _to_iso(doc["createdAt"])
    if "updatedAt" in doc:
        doc["updatedAt"] = _to_iso(doc["updatedAt"])
    if "fechaEntrega" in doc:
        doc["fechaEntrega"] = _to_iso(doc["fechaEntrega"])
    
    # Serializar pagos
    if "pagos" in doc:
        for pago in doc["pagos"]:
            if "fecha" in pago:
                pago["fecha"] = _to_iso(pago["fecha"])
            if "fechaAprobacion" in pago:
                pago["fechaAprobacion"] = _to_iso(pago["fechaAprobacion"])
            if "fechaRechazo" in pago:
                pago["fechaRechazo"] = _to_iso(pago["fechaRechazo"])
    
    # Serializar timeline
    if "timeline" in doc:
        for event in doc["timeline"]:
            if "ts" in event:
                event["ts"] = _to_iso(event["ts"])
    
    # Asegurar floats en costos
    if "costos" in doc:
        for k, v in doc["costos"].items():
            if isinstance(v, (int, float)):
                doc["costos"][k] = float(v)
    
    # Serializar items
    if "items" in doc:
        for item in doc["items"]:
            if "productId" in item:
                item["productId"] = str(item["productId"])
            if "precioUnitario" in item:
                item["precioUnitario"] = float(item["precioUnitario"])
            if "ficha_id" in item and item["ficha_id"]:
                item["ficha_id"] = str(item["ficha_id"])
    
    # ✅ Agregar información calculada de pago (con manejo de errores)
    try:
        totales = calcular_totales_pago(doc)
        doc["infoPago"] = totales
    except Exception as e:
        # Si falla el cálculo, proporcionar valores por defecto
        current_app.logger.warning(f"Error al calcular totales de pago: {str(e)}")
        doc["infoPago"] = {
            "total_pedido": doc.get("costos", {}).get("total", 0),
            "total_pagado": 0,
            "saldo_pendiente": doc.get("costos", {}).get("total", 0),
            "porcentaje_pagado": 0,
            "estado_pago": "pago_pendiente"
        }
    
    return doc



def _serialize_list(docs: list) -> list:
    return [_serialize(d) for d in docs]

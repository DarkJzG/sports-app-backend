# flask_api/modelo/modelo_pedido.py
from flask import current_app
from bson import ObjectId
from datetime import datetime, timezone

ESTADOS_PEDIDO = [
    # Estados de pago
    "pendiente_pago",   # creado; con pago por transfer. aún sin validar/confirmar
    "pagado_parcial",   # anticipo recibido
    "pagado_total",     # total recibido

    # Flujo de producción / logística
    "en_produccion",
    "listo",
    "enviado",
    "entregado",

    # Otros
    "cancelado",
    "fallido",

]

def get_pedidos_collection():
    return current_app.mongo.db.pedidos

def _now_utc():
    return datetime.now(timezone.utc)

def build_pedido_doc(user_id: str, data: dict) -> dict:
    tipo_pago = data.get("tipoPago", "completo")
    total = float(data["costos"]["total"])

    # Calcular montos según el tipo de pago
    if tipo_pago == "anticipo":
        monto_anticipo = round(total * 0.5, 2)  # 50% de anticipo
        saldo_pendiente = round(total - monto_anticipo, 2)
        estado = "pendiente_pago"
    else:
        monto_anticipo = total
        saldo_pendiente = 0.0
        estado = "pagado_total"

    direccion = data["direccionEnvio"]
    tipo_envio = direccion.get("tipoEnvio", "domicilio")

    # Construir el documento del pedido
    pedido_doc = {
        "userId": ObjectId(user_id),
        "items": [
            {
                "productId": ObjectId(item["productId"]),
                "nombre": item["nombre"],
                "cantidad": int(item["cantidad"]),
                "precioUnitario": float(item["precioUnitario"]),
                "talla": item.get("talla"),
                "color": item.get("color"),
                "imagen": item.get("imagen")
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
        "montoPagado": monto_anticipo if tipo_pago == "anticipo" else total,
        "saldoPendiente": saldo_pendiente if tipo_pago == "anticipo" else 0.0,
        "costos": {
            "subtotal": float(data["costos"]["subtotal"]),
            "envio": float(data["costos"]["envio"]),
            "impuestos": float(data["costos"]["impuestos"]),
            "total": float(data["costos"]["total"]),
        },
        "estado": estado,
        "pagos": [],  # Nuevo array para historial de pagos
        "createdAt": _now_utc(),
        "updatedAt": _now_utc(),
        "timeline": [
            {
                "evento": "creado",
                "estado": estado,
                "ts": _now_utc(),
                "nota": "Pedido creado" + ("" if estado == "pendiente_pago" else " con pago completo")
            }
        ],
    }

    # Si hay un comprobante de transferencia, agregarlo como primer pago
    if "imagenTransferencia" in data:
        pago = {
            "monto": monto_anticipo if tipo_pago == "anticipo" else total,
            "fecha": _now_utc(),
            "referencia": data.get("referenciaPago", "Pago inicial"),
            "comprobante": data["imagenTransferencia"],
            "tipo": "anticipo" if tipo_pago == "anticipo" else "completo",
            "estado": "aprobado",
            "nota": "Pago inicial del pedido"
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
            "usuario.password": 0,  # nunca enviar password
        }}
    ]

    cursor = col.aggregate(pipeline)
    items = list(cursor)
    total = col.count_documents(filt)
    return _serialize_list(items), total


def update_pedido_status(pedido_id: str, nuevo_estado: str, nota_admin: str = None):
    if nuevo_estado not in ESTADOS_PEDIDO:
        raise ValueError("Estado inválido")

    col = get_pedidos_collection()
    upd = {
        "$set": {"estado": nuevo_estado, "updatedAt": _now_utc()},
        "$push": {"timeline": {"evento": "cambio_estado", "estado": nuevo_estado, "nota": nota_admin, "ts": _now_utc()}}
    }
    res = col.update_one({"_id": ObjectId(pedido_id)}, upd)
    return res.modified_count == 1

def _to_iso(dt):
    try:
        return dt.isoformat()
    except Exception:
        return dt

# En la función _serialize, asegúrate de incluir el campo imagenComprobante
def _serialize(doc: dict) -> dict:
    if not doc:
        return None
        
    doc["_id"] = str(doc["_id"])
    doc["userId"] = str(doc["userId"])
    
    # Serializar pagos si existen
    if "pagos" in doc:
        for pago in doc["pagos"]:
            pago["fecha"] = _to_iso(pago["fecha"])
    
    # Serializar timeline
    if "timeline" in doc:
        for event in doc["timeline"]:
            event["ts"] = _to_iso(event["ts"])
    
    # Asegurarse de que los campos de costo sean float
    if "costos" in doc:
        for k, v in doc["costos"].items():
            if isinstance(v, (int, float)):
                doc["costos"][k] = float(v)
    
    # Asegurarse de que los items tengan los campos correctos
    if "items" in doc:
        for item in doc["items"]:
            item["productId"] = str(item["productId"])
            if "precioUnitario" in item:
                item["precioUnitario"] = float(item["precioUnitario"])
    
    return doc

def _serialize_list(docs: list) -> list:
    return [_serialize(d) for d in docs]

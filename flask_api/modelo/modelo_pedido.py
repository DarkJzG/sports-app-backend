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
    tipo_pago = data.get("tipoPago", "completo")  # completo o anticipo
    total = float(data["costos"]["total"])
    
    if tipo_pago == "anticipo":
        monto_pagado = round(total * 0.5, 2)
        saldo_pendiente = total - monto_pagado
    else:
        monto_pagado = total
        saldo_pendiente = 0.0

    return {
        "userId": ObjectId(user_id),
        "items": [
            {
                "productId": ObjectId(i["productId"]),
                "nombre": i["nombre"],
                "cantidad": int(i["cantidad"]),
                "precioUnitario": float(i["precioUnitario"]),
                "imagen": i.get("imagen"),
                "talla": i.get("talla"),
                "color": i.get("color"),  # puede ser dict (como vienes enviando)
            } for i in data["items"]
        ],
        "direccionEnvio": data["direccionEnvio"],
        "metodoPago": data.get("metodoPago", "transferencia"),
        "tipoPago": tipo_pago,
        "montoPagado": monto_pagado,
        "saldoPendiente": saldo_pendiente,
        "costos": {
            "subtotal": float(data["costos"]["subtotal"]),
            "envio": float(data["costos"]["envio"]),
            "impuestos": float(data["costos"]["impuestos"]),
            "total": float(data["costos"]["total"]),
        },
        "estado": "pendiente_pago",
        "referenciasPago": [
            {
                "monto": monto_pagado,
                "referencia": data.get("referenciaPago"),
                "fecha": _now_utc(),
                "presencial": bool(data.get("presencial", False)),
            }
        ],
        "createdAt": _now_utc(),
        "updatedAt": _now_utc(),
        "timeline": [
            {"evento": "creado", "estado": "pendiente_pago", "ts": _now_utc()}
        ],
    }



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
    cursor = col.find(filt).sort("createdAt", -1).skip(skip).limit(limit)
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

def _serialize(doc: dict) -> dict:
    if not doc:
        return None
    doc["_id"] = str(doc["_id"])
    doc["userId"] = str(doc["userId"])
    # fechas
    if "createdAt" in doc: doc["createdAt"] = _to_iso(doc["createdAt"])
    if "updatedAt" in doc: doc["updatedAt"] = _to_iso(doc["updatedAt"])
    # timeline
    for ev in doc.get("timeline", []):
        if "ts" in ev:
            ev["ts"] = _to_iso(ev["ts"])
    # pagos
    for ref in doc.get("referenciasPago", []):
        if "fecha" in ref:
            ref["fecha"] = _to_iso(ref["fecha"])
    # items
    for it in doc.get("items", []):
        if "productId" in it and isinstance(it["productId"], ObjectId):
            it["productId"] = str(it["productId"])
    return doc


def _serialize_list(docs: list) -> list:
    return [_serialize(d) for d in docs]

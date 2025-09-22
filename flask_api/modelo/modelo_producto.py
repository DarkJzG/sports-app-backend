from flask import current_app
from bson import ObjectId

def get_producto_collection():
    return current_app.mongo.db.productos

def descontar_stock_producto(product_id: str, cantidad: int, talla: str = None, color: str = None):
    """
    Intenta descontar stock a nivel de variante (talla/color) si existen,
    en caso contrario descuenta del stock global del producto.

    Retorna True si descuenta, False si no hay stock suficiente.
    """
    col = get_producto_collection()
    _id = ObjectId(product_id)
    
    # 1) Intento variante
    if talla or color:
        # Estructura esperada: variantes: [{talla, color, stock}]
        res = col.update_one(
            {
                "_id": _id,
                "variantes": {
                    "$elemMatch": {
                        **({"talla": talla} if talla else {}),
                        **({"color": color} if color else {}),
                        "stock": {"$gte": cantidad}
                    }
                }
            },
            {"$inc": {"variantes.$.stock": -cantidad}}
        )
        if res.modified_count == 1:
            return True

    # 2) Stock global
    res2 = col.update_one({"_id": _id, "stock": {"$gte": cantidad}}, {"$inc": {"stock": -cantidad}})
    return res2.modified_count == 1
# flask_api/modelo/modelo_carrito.py
from flask import current_app
from bson.objectid import ObjectId

class ModeloCarrito:

    @staticmethod
    def agregar_carrito(data):
        return current_app.mongo.db.carrito.insert_one(data)

    @staticmethod
    def obtener_carrito_usuario(user_id):
        items = list(current_app.mongo.db.carrito.find(
            {"userId": user_id, "estado": "pendiente"}
        ))
        # Convertir ObjectId a string para _id, productoId y ficha_id
        for item in items:
            item['_id'] = str(item['_id'])
            if 'productoId' in item and item['productoId'] is not None:
                item['productoId'] = str(item['productoId'])
            if 'ficha_id' in item and item['ficha_id'] is not None:
                item['ficha_id'] = str(item['ficha_id'])
        return items

    @staticmethod
    def obtener_item_por_id(item_id):
        try:
            return current_app.mongo.db.carrito.find_one({"_id": ObjectId(item_id)})
        except Exception as e:
            print("❌ Error en obtener_item_por_id:", e)
            return None

    @staticmethod
    def eliminar_item_carrito(item_id):
        return current_app.mongo.db.carrito.delete_one({"_id": ObjectId(item_id)})

    @staticmethod
    def vaciar_carrito_usuario(user_id):
        return current_app.mongo.db.carrito.delete_many(
            {"userId": user_id, "estado": "pendiente"}
        )

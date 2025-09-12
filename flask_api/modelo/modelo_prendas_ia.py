from flask import current_app
from bson.objectid import ObjectId

class ModeloPrendasIA:

    @staticmethod
    def crear_prenda(data):
        """
        Guarda una prenda generada por IA
        """
        return current_app.mongo.db.prendas.insert_one(data)

    @staticmethod
    def obtener_todas(user_id=None):
        query = {}
        if user_id:
            query["user_id"] = ObjectId(user_id)
        return list(current_app.mongo.db.prendas.find(query).sort("tipo_prenda", 1))


    @staticmethod
    def obtener_por_id(prenda_id):
        try:
            return current_app.mongo.db.prendas.find_one({"_id": ObjectId(prenda_id)})
        except Exception as e:
            print("Error al buscar prenda:", e)
            return None

    @staticmethod
    def actualizar_prenda(prenda_id, data):
        return current_app.mongo.db.prendas.update_one(
            {"_id": ObjectId(prenda_id)},
            {"$set": data}
        )

    @staticmethod
    def eliminar_prenda(prenda_id):
        return current_app.mongo.db.prendas.delete_one({"_id": ObjectId(prenda_id)})

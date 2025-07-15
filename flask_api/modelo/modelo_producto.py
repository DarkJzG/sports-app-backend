from flask import current_app

def get_producto_collection():
    return current_app.mongo.db.productos

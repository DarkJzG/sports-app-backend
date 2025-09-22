# flask_api/modelo/modelo_mano_obra.py

from flask import current_app

def get_mano_obra_collection():
    """Retorna la colección de mano_obra"""
    return current_app.mongo.db.mano_obra



from flask import current_app

def get_categorias_collection():
    """
    Retorna la colección de categorías de producto (catg_prod)
    """
    return current_app.mongo.db.catg_prod

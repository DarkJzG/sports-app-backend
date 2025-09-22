

from flask import current_app

def get_categorias_collection():

    return current_app.mongo.db.catg_prod

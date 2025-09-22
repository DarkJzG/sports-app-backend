# flask_api/modelo/modelo_catg_tela.py
from flask import current_app

def get_catg_tela_collection():
    return current_app.mongo.db.catg_tela

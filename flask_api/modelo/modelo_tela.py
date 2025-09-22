from flask import current_app

def get_telas_collection():
    return current_app.mongo.db.telas

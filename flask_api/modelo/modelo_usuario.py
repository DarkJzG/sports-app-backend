from flask import current_app

def get_users_collection():
    return current_app.mongo.db.users

def get_direcciones_collection():
    return current_app.mongo.db.direcciones
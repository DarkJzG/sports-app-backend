from flask import current_app

def get_users_collection():
    return current_app.mongo.db.users


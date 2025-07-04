from pymongo import MongoClient

# Pon aquí tu cadena de conexión real
uri = "mongodb+srv://1djohanburbano:6rsVRkmjkrmWv4Ic@cluster0.vujwwmh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri)
db = client.test  # Puedes usar la base de datos "test" para probar

print(db.list_collection_names())

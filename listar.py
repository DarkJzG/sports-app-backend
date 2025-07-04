from pymongo import MongoClient

uri = "mongodb+srv://1djohanburbano:6rsVRkmjkrmWv4Ic@cluster0.vujwwmh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client['tienda']
productos = db['productos']

# Insertar un producto de ejemplo
nuevo_producto = {
    "nombre": "Camiseta deportiva",
    "descripcion": "Camiseta transpirable para entrenamiento",
    "precio": 19.99,
    "stock": 50,
    "talla": ["S", "M", "L", "XL"],
    "color": "Azul",
    "imagen_url": "https://tuservidor.com/imagen.png"
}
resultado = productos.insert_one(nuevo_producto)
print("Producto insertado con id:", resultado.inserted_id)

# Consultar todos los productos
todos = productos.find()
print("Lista de productos:")
for producto in todos:
    print(producto)

from pymongo import MongoClient

# Cadena de conexión
uri = "mongodb+srv://1djohanburbano:6rsVRkmjkrmWv4Ic@cluster0.vujwwmh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)

# Selecciona la base de datos (puedes cambiar 'tienda' por el nombre que prefieras)
db = client['tienda']

# Selecciona la colección de productos
productos = db['productos']

# Producto de ejemplo
nuevo_producto = {
    "nombre": "Camiseta deportiva",
    "descripcion": "Camiseta transpirable para entrenamiento",
    "precio": 19.99,
    "stock": 50,
    "talla": ["S", "M", "L", "XL"],
    "color": "Azul",
    "imagen_url": "https://tuservidor.com/imagen.png"
}

# Inserta el producto
resultado = productos.insert_one(nuevo_producto)
print("Producto insertado con id:", resultado.inserted_id)

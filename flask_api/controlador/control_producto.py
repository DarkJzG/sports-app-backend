# flask_api/controlador/control_producto.py

from flask import jsonify, request
from flask_api.modelo.modelo_producto import get_producto_collection
from datetime import datetime
from bson import ObjectId

# -------------------------------
# Crear producto
# -------------------------------
def crear_producto():
    data = request.get_json()

    nombre = data.get("nombre")
    categoria_id = data.get("categoria_id")
    tela_id = data.get("tela_id")
    color = data.get("color")
    imagen_url = data.get("imagen_url")
    genero = data.get("genero", "unisex")

    if not nombre or not categoria_id or not tela_id or not imagen_url or not (color and color.get("lote_id")):
        return jsonify({"ok": False, "msg": "Faltan campos obligatorios"}), 400


    doc = {
        "nombre": nombre,
        "observaciones": data.get("observaciones", ""),
        "categoria_id": categoria_id,
        "categoria_nombre": data.get("categoria_nombre"),
        "tela_id": tela_id,
        "tela_nombre": data.get("tela_nombre"),
        "color": color,  
        "tallas_disponibles": data.get("tallas_disponibles", []),
        "genero": genero,

        "mano_obra_id": data.get("mano_obra_id"),
        "mano_obra_prenda": float(data.get("mano_obra_prenda", 0)),
        "insumos": data.get("insumos", []),

        "cantDisenos": data.get("cantDisenos", {}),
        "costos": data.get("costos", {"tela": 0, "manoObra": 0, "disenos": 0, "total": 0}),

        "precio_venta": float(data.get("precio_venta", 0)),
        "ganancia_menor": float(data.get("ganancia_menor", 0)),
        "ganancia_mayor": float(data.get("ganancia_mayor", 0)),

        "imagen_url": imagen_url,
        "estado": "activo",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    col = get_producto_collection()
    result = col.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return jsonify({"ok": True, "msg": "Producto creado", "producto": doc})

# -------------------------------
# Listar todos los productos
# -------------------------------
def listar_productos():
    col = get_producto_collection()
    lista = list(col.find({}))
    for p in lista:
        p["_id"] = str(p["_id"])
    return jsonify(lista)

# -------------------------------
# Obtener producto por ID
# -------------------------------
def obtener_producto(id):
    col = get_producto_collection()
    producto = col.find_one({"_id": ObjectId(id)})
    if not producto:
        return jsonify({"ok": False, "msg": "No encontrado"}), 404
    producto["_id"] = str(producto["_id"])
    return jsonify(producto)

# -------------------------------
# Actualizar producto
# -------------------------------
def actualizar_producto(id):
    data = request.get_json()
    update_data = {}

    campos = [
        "nombre", "observaciones", "categoria_id", "categoria_nombre",
        "tela_id", "tela_nombre", "color", "tallas_disponibles", "genero",
        "mano_obra_id", "mano_obra_prenda", "insumos", "cantDisenos",
        "costos", "precio_venta", "ganancia_menor", "ganancia_mayor",
        "imagen_url", "estado"
    ]

    for campo in campos:
        if campo in data:
            update_data[campo] = data[campo]

    update_data["updated_at"] = datetime.utcnow()

    col = get_producto_collection()
    col.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    return jsonify({"ok": True, "msg": "Producto actualizado"})

# -------------------------------
# Eliminar producto
# -------------------------------
def eliminar_producto(id):
    col = get_producto_collection()
    result = col.delete_one({"_id": ObjectId(id)})
    if result.deleted_count:
        return jsonify({"ok": True, "msg": "Producto eliminado"})
    else:
        return jsonify({"ok": False, "msg": "No encontrado"}), 404


def listar_por_categoria(categoria_id):
    col = get_producto_collection()
    productos = list(col.find({"categoria_id": categoria_id, "estado": "activo"}))
    for p in productos:
        p["_id"] = str(p["_id"])
    return jsonify(productos)
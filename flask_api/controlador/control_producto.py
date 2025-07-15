from flask import jsonify, request
from flask_api.modelo.modelo_producto import get_producto_collection
from datetime import datetime

# Crear producto/prenda final
def crear_producto():
    data = request.get_json()
    col = get_producto_collection()

    color_info = {
        'namediseno': data.get('namediseno'),
        'diseno': float(data.get('diseno', 0)),
        'metrocantidad': float(data.get('metrocantidad', 0)),
        'costounitario': float(data.get('costounitario', 0)),
        'costoxmayor': float(data.get('costoxmayor', 0)),
        'preciomenor': float(data.get('preciomenor', 0)),
        'preciomayor': float(data.get('preciomayor', 0)),
        'ganamenor': float(data.get('ganamenor', 0)),
        'ganamayor': float(data.get('ganamayor', 0))
    }

    nuevo_producto = {
        'nombre': data.get('nombre'),
        'categoria': data.get('categoria'),
        'tela': data.get('tela'),
        'manoobra': float(data.get('manoobra', 0)),
        'color': [color_info],  # importante: como lista
        'imageUrl': data.get('imageUrl'),
        'createdAt': datetime.utcnow()
    }

    col.insert_one(nuevo_producto)
    return jsonify({'ok': True, 'msg': 'Producto/prenda guardado correctamente.'})

# Listar productos/prendas
def listar_productos():
    col = get_producto_collection()
    productos = list(col.find({}))
    for p in productos:
        p['_id'] = str(p['_id'])
    return jsonify(productos)

# Obtener uno por id
def obtener_producto(id):
    from bson import ObjectId
    col = get_producto_collection()
    p = col.find_one({'_id': ObjectId(id)})
    if not p:
        return jsonify({'ok': False, 'msg': 'No encontrado'}), 404
    p['_id'] = str(p['_id'])
    return jsonify(p)

# Actualizar producto/prenda
def actualizar_producto(id):
    from bson import ObjectId
    data = request.get_json()

    color_info = {
        'namediseno': data.get('namediseno'),
        'diseno': float(data.get('diseno', 0)),
        'metrocantidad': float(data.get('metrocantidad', 0)),
        'costounitario': float(data.get('costounitario', 0)),
        'costoxmayor': float(data.get('costoxmayor', 0)),
        'preciomenor': float(data.get('preciomenor', 0)),
        'preciomayor': float(data.get('preciomayor', 0)),
        'ganamenor': float(data.get('ganamenor', 0)),
        'ganamayor': float(data.get('ganamayor', 0))
    }

    update_data = {
        'nombre': data.get('nombre'),
        'categoria': data.get('categoria'),
        'tela': data.get('tela'),
        'manoobra': float(data.get('manoobra', 0)),
        'color': [color_info],
        'imageUrl': data.get('imageUrl')
    }

    col = get_producto_collection()
    col.update_one({'_id': ObjectId(id)}, {'$set': update_data})
    return jsonify({'ok': True, 'msg': 'Producto actualizado'})

# Eliminar producto/prenda
def eliminar_producto(id):
    from bson import ObjectId
    col = get_producto_collection()
    result = col.delete_one({'_id': ObjectId(id)})
    if result.deleted_count:
        return jsonify({'ok': True, 'msg': 'Eliminado'})
    else:
        return jsonify({'ok': False, 'msg': 'No encontrado'}), 404

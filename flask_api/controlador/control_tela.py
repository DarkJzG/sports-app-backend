# flask_api/controlador/control_tela.py
from flask import jsonify, request
from flask_api.modelo.modelo_tela import get_telas_collection
from bson import ObjectId

# Crear tela con múltiples colores
def crear_tela():
    data = request.get_json()
    nombre = data.get('nombre')
    colores = data.get('colores', [])
    cantidad = float(data.get('cantidad', 0))
    precio_metro = float(data.get('precio_metro', 0))
    imagen_url = data.get('imagen_url')

    if not nombre or not colores or not imagen_url:
        return jsonify({'ok': False, 'msg': 'Datos incompletos'}), 400

    for color in colores:
        if 'nombre' not in color or 'codigo' not in color:
            return jsonify({'ok': False, 'msg': 'Formato de color inválido'}), 400

    col = get_telas_collection()
    col.insert_one({
        'nombre': nombre,
        'colores': colores,
        'cantidad': cantidad,
        'precio_metro': precio_metro,
        'imagen_url': imagen_url
    })
    return jsonify({'ok': True, 'msg': 'Tela agregada'})


def listar_telas():
    col = get_telas_collection()
    lista = list(col.find({}))
    for tela in lista:
        tela['_id'] = str(tela['_id'])  # convierte ObjectId a str
    return jsonify(lista)

def obtener_tela(id):
    from bson import ObjectId
    col = get_telas_collection()
    tela = col.find_one({'_id': ObjectId(id)})
    if not tela:
        return jsonify({'ok': False, 'msg': 'Tela no encontrada'}), 404
    tela['_id'] = str(tela['_id'])
    return jsonify(tela)

def actualizar_tela(id):
    from bson import ObjectId
    data = request.get_json()

    update_fields = {}
    if 'nombre' in data: update_fields['nombre'] = data['nombre']
    if 'colores' in data: 
        # Validar colores
        if isinstance(data['colores'], list):
            for c in data['colores']:
                if 'nombre' not in c or 'codigo' not in c:
                    return jsonify({'ok': False, 'msg': 'Formato de color inválido'}), 400
            update_fields['colores'] = data['colores']
    if 'cantidad' in data: update_fields['cantidad'] = float(data['cantidad'])
    if 'precio_metro' in data: update_fields['precio_metro'] = float(data['precio_metro'])
    if 'imagen_url' in data: update_fields['imagen_url'] = data['imagen_url']

    col = get_telas_collection()
    col.update_one({'_id': ObjectId(id)}, {'$set': update_fields})
    return jsonify({'ok': True, 'msg': 'Tela actualizada'})

def eliminar_tela(id):
    from bson import ObjectId
    col = get_telas_collection()
    result = col.delete_one({'_id': ObjectId(id)})
    if result.deleted_count:
        return jsonify({'ok': True, 'msg': 'Tela eliminada'})
    else:
        return jsonify({'ok': False, 'msg': 'No encontrada'}), 404

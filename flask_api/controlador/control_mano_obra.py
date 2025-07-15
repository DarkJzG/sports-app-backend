# flask_api/controlador/control_mano_obra.py

from flask import jsonify, request
from flask_api.modelo.modelo_mano_obra import get_mano_obra_collection

# Crear mano de obra
def crear_mano_obra():
    data = request.get_json()
    categoria_id = data.get('categoria_id')
    categoria_nombre = data.get('categoria_nombre')

    # Insumos principales
    insumo_hilo = float(data.get('insumo_hilo', 0))     
    insumo_mano_obra = float(data.get('insumo_mano_obra', 0))
    insumo_elastico = float(data.get('insumo_elastico', 0))
    insumo_cierre = float(data.get('insumo_cierre', 0))

    # Diseño: NO sumar a total
    bordado = float(data.get('bordado', 0))
    estampado = float(data.get('estampado', 0))
    sublimado = float(data.get('sublimado', 0))

    total = insumo_hilo + insumo_mano_obra + insumo_elastico + insumo_cierre

    if not categoria_id:
        return jsonify({'ok': False, 'msg': 'Falta la categoría'}), 400

    col = get_mano_obra_collection()
    col.insert_one({
        'categoria_id': categoria_id,
        'categoria_nombre': categoria_nombre,
        'insumo_hilo': insumo_hilo,
        'insumo_mano_obra': insumo_mano_obra,
        'insumo_elastico': insumo_elastico,
        'insumo_cierre': insumo_cierre,
        'total': total,
        'bordado': bordado,
        'estampado': estampado,
        'sublimado': sublimado
    })
    return jsonify({'ok': True, 'msg': 'Mano de obra agregada'})

# Listar mano de obra
def listar_mano_obra():
    col = get_mano_obra_collection()
    lista = list(col.find({}))
    for m in lista:
        m['_id'] = str(m['_id'])
    return jsonify(lista)

# Obtener una mano de obra por id
def obtener_mano_obra(id):
    from bson import ObjectId
    col = get_mano_obra_collection()
    mano = col.find_one({'_id': ObjectId(id)})
    if not mano:
        return jsonify({'ok': False, 'msg': 'No encontrada'}), 404
    mano['_id'] = str(mano['_id'])
    return jsonify(mano)

# Actualizar mano de obra
def actualizar_mano_obra(id):
    from bson import ObjectId
    data = request.get_json()
    update_data = {k: float(v) if 'insumo' in k or k == 'total' else v for k, v in data.items() if v is not None}
    # recalcular total si algún insumo cambió
    if any(k.startswith('insumo') for k in update_data):
        total = sum(float(update_data.get(f, 0)) for f in ['insumo_hilo','insumo_mano_obra','insumo_elastico','insumo_cierre'])
        update_data['total'] = total
    col = get_mano_obra_collection()
    col.update_one({'_id': ObjectId(id)}, {'$set': update_data})
    return jsonify({'ok': True, 'msg': 'Mano de obra actualizada'})

# Eliminar mano de obra
def eliminar_mano_obra(id):
    from bson import ObjectId
    col = get_mano_obra_collection()
    result = col.delete_one({'_id': ObjectId(id)})
    if result.deleted_count:
        return jsonify({'ok': True, 'msg': 'Eliminada'})
    else:
        return jsonify({'ok': False, 'msg': 'No encontrada'}), 404

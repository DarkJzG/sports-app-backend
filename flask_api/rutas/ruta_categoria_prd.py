
from flask import Blueprint, jsonify, request
from flask_api.controlador.control_categoria_prd import crear_categoria
from flask_api.modelo.modelo_categoria_prd import get_categorias_collection

catg_bp = Blueprint('catg', __name__, url_prefix='/catg')

@catg_bp.route('/add', methods=['POST'])
def add_categoria():
    return crear_categoria()


from flask_api.controlador.control_categoria_prd import listar_categorias

@catg_bp.route('/all', methods=['GET'])
def get_categorias():
    return listar_categorias()


from bson import ObjectId

@catg_bp.route('/delete/<id>', methods=['DELETE'])
def delete_categoria(id):
    catg = get_categorias_collection()
    result = catg.delete_one({'_id': ObjectId(id)})
    if result.deleted_count:
        return jsonify({'ok': True, 'msg': 'Categoría eliminada'})
    else:
        return jsonify({'ok': False, 'msg': 'No encontrada'}), 404


@catg_bp.route('/update/<id>', methods=['PUT'])
def update_categoria(id):
    data = request.get_json()
    nombre = data.get('nombre')
    descripcion = data.get('descripcion')
    imagen_url = data.get('imagen_url')
    catg = get_categorias_collection()
    update_data = {k: v for k, v in {
        'nombre': nombre, 'descripcion': descripcion, 'imagen_url': imagen_url
    }.items() if v is not None}
    catg.update_one({'_id': ObjectId(id)}, {'$set': update_data})
    return jsonify({'ok': True, 'msg': 'Categoría actualizada'})


@catg_bp.route('/get/<id>', methods=['GET'])
def get_categoria(id):
    catg = get_categorias_collection()
    cat = catg.find_one({'_id': ObjectId(id)})
    if not cat:
        return jsonify({'ok': False, 'msg': 'No encontrada'}), 404
    cat['_id'] = str(cat['_id'])
    return jsonify(cat)

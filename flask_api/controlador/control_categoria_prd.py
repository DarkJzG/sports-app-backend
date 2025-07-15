
from flask import jsonify, request
from flask_api.modelo.modelo_categoria_prd import get_categorias_collection

def crear_categoria():
    data = request.get_json()
    nombre = data.get('nombre')
    descripcion = data.get('descripcion')
    imagen_url = data.get('imagen_url')  # la URL de Cloudinary

    if not nombre or not descripcion or not imagen_url:
        return jsonify({'ok': False, 'msg': 'Datos incompletos'}), 400

    catg = get_categorias_collection()
    catg.insert_one({
        "nombre": nombre,
        "descripcion": descripcion,
        "imagen_url": imagen_url
    })
    return jsonify({'ok': True, 'msg': 'Categoría creada'})


##Obtener las categorias de MongoDB
def listar_categorias():
    catg = get_categorias_collection()
    categorias = list(catg.find({}))
    # Serializa el ObjectId
    for c in categorias:
        c['_id'] = str(c['_id'])
    return jsonify(categorias)




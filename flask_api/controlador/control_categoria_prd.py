# flask_api/controlador/control_categoria_prd.py
from flask import jsonify, request
from flask_api.modelo.modelo_categoria_prd import get_categorias_collection
from datetime import datetime
from bson import ObjectId

# Crear categoría de producto
def crear_categoria():
    data = request.get_json()
    nombre = data.get('nombre')
    descripcion = data.get('descripcion')
    imagen_url = data.get('imagen_url')
    insumos = data.get('insumos_posibles', [])

    if not nombre or not descripcion or not imagen_url:
        return jsonify({'ok': False, 'msg': 'Datos incompletos'}), 400

    col = get_categorias_collection()

    if col.find_one({"nombre": nombre}):
        return jsonify({'ok': False, 'msg': 'Ya existe una categoría con ese nombre'}), 400

    nueva_cat = {
        "nombre": nombre,
        "descripcion": descripcion,
        "imagen_url": imagen_url,
        "estado": "activo",
        "insumos_posibles": insumos,   # 🔹 NUEVO
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    result = col.insert_one(nueva_cat)
    nueva_cat["_id"] = str(result.inserted_id)
    return jsonify({'ok': True, 'msg': 'Categoría creada', 'categoria': nueva_cat})



# Listar categorías
def listar_categorias():
    col = get_categorias_collection()
    categorias = list(col.find({}))
    for c in categorias:
        c["_id"] = str(c["_id"])
    return jsonify(categorias)


# Obtener una categoría
def obtener_categoria(id):
    col = get_categorias_collection()
    cat = col.find_one({"_id": ObjectId(id)})
    if not cat:
        return jsonify({'ok': False, 'msg': 'No encontrada'}), 404
    cat["_id"] = str(cat["_id"])
    return jsonify(cat)


# Actualizar categoría
def actualizar_categoria(id):
    data = request.get_json()
    update_fields = {}

    if "nombre" in data:
        update_fields["nombre"] = data["nombre"]
    if "descripcion" in data:
        update_fields["descripcion"] = data["descripcion"]
    if "imagen_url" in data:
        update_fields["imagen_url"] = data["imagen_url"]
    if "insumos_posibles" in data:
        update_fields["insumos_posibles"] = data["insumos_posibles"]

    update_fields["updated_at"] = datetime.utcnow()

    col = get_categorias_collection()
    col.update_one({"_id": ObjectId(id)}, {"$set": update_fields})
    return jsonify({'ok': True, 'msg': 'Categoría actualizada'})



# Eliminar categoría
def eliminar_categoria(id):
    col = get_categorias_collection()
    result = col.delete_one({"_id": ObjectId(id)})
    if result.deleted_count:
        return jsonify({'ok': True, 'msg': 'Categoría eliminada'})
    else:
        return jsonify({'ok': False, 'msg': 'No encontrada'}), 404

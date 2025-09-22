# flask_api/controlador/control_mano_obra.py

from flask import jsonify, request
from flask_api.modelo.modelo_mano_obra import get_mano_obra_collection
from datetime import datetime
from bson import ObjectId

# -------------------------------
# Crear mano de obra
# -------------------------------
def crear_mano_obra():
    data = request.get_json()
    categoria_id = data.get("categoria_id")
    categoria_nombre = data.get("categoria_nombre")

    insumos = data.get("insumos", [])  
    disenos = data.get("disenos", {})  
    mano_obra_prenda = float(data.get("mano_obra_prenda", 0))

    if not categoria_id or not categoria_nombre:
        return jsonify({"ok": False, "msg": "Faltan datos de la categoría"}), 400

    insumos_total = sum(float(insumo.get("costo", 0)) for insumo in insumos)
    total = insumos_total + mano_obra_prenda   # 👈 sumar mano de obra, no diseños

    doc = {
        "categoria_id": categoria_id,
        "categoria_nombre": categoria_nombre,
        "insumos": insumos,
        "disenos": {
            "logo_bordado_grande": float(disenos.get("logo_bordado_grande", 0)),
            "logo_bordado_pequeno": float(disenos.get("logo_bordado_pequeno", 0)),
            "logo_estampado_grande": float(disenos.get("logo_estampado_grande", 0)),
            "logo_estampado_pequeno": float(disenos.get("logo_estampado_pequeno", 0)),
            "sublimado": float(disenos.get("sublimado", 0)),
        },
        "mano_obra_prenda": mano_obra_prenda,
        "insumosTotal": insumos_total,      # 👈 extra para frontend
        "total_mano_obra": mano_obra_prenda, # 👈 extra para frontend
        "total": total,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    col = get_mano_obra_collection()
    result = col.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return jsonify({"ok": True, "msg": "Mano de obra creada", "mano": doc})


def listar_mano_obra():
    col = get_mano_obra_collection()
    lista = list(col.find({}))
    for m in lista:
        m["_id"] = str(m["_id"])
        # asegurar campos siempre existen
        m["insumosTotal"] = m.get("insumosTotal", sum(float(i.get("costo", 0)) for i in m.get("insumos", [])))
        m["total_mano_obra"] = m.get("total_mano_obra", m.get("mano_obra_prenda", 0))
    return jsonify(lista)


# -------------------------------
# Obtener una mano de obra por ID
# -------------------------------
def obtener_mano_obra(id):
    col = get_mano_obra_collection()
    mano = col.find_one({"_id": ObjectId(id)})
    if not mano:
        return jsonify({"ok": False, "msg": "No encontrada"}), 404
    mano["_id"] = str(mano["_id"])
    return jsonify(mano)


# -------------------------------
# Actualizar mano de obra
# -------------------------------
def actualizar_mano_obra(id):
    data = request.get_json()
    update_data = {}

    if "categoria_id" in data:
        update_data["categoria_id"] = data["categoria_id"]
    if "categoria_nombre" in data:
        update_data["categoria_nombre"] = data["categoria_nombre"]

    insumos = data.get("insumos", [])
    mano_obra_prenda = float(data.get("mano_obra_prenda", 0))

    if insumos:
        update_data["insumos"] = insumos
    if "disenos" in data:
        disenos = data["disenos"]
        update_data["disenos"] = {
            "logo_bordado_grande": float(disenos.get("logo_bordado_grande", 0)),
            "logo_bordado_pequeno": float(disenos.get("logo_bordado_pequeno", 0)),
            "logo_estampado_grande": float(disenos.get("logo_estampado_grande", 0)),
            "logo_estampado_pequeno": float(disenos.get("logo_estampado_pequeno", 0)),
            "sublimado": float(disenos.get("sublimado", 0)),
        }

    # Recalcular totales
    insumos_total = sum(float(insumo.get("costo", 0)) for insumo in insumos)
    total = insumos_total + mano_obra_prenda

    update_data["mano_obra_prenda"] = mano_obra_prenda
    update_data["insumosTotal"] = insumos_total
    update_data["total_mano_obra"] = mano_obra_prenda
    update_data["total"] = total
    update_data["updated_at"] = datetime.utcnow()

    col = get_mano_obra_collection()
    col.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    return jsonify({"ok": True, "msg": "Mano de obra actualizada"})


# -------------------------------
# Eliminar mano de obra
# -------------------------------
def eliminar_mano_obra(id):
    col = get_mano_obra_collection()
    result = col.delete_one({"_id": ObjectId(id)})
    if result.deleted_count:
        return jsonify({"ok": True, "msg": "Eliminada"})
    else:
        return jsonify({"ok": False, "msg": "No encontrada"}), 404

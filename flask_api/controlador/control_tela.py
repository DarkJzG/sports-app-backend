# flask_api/controlador/control_tela.py
from flask import jsonify, request
from flask_api.modelo.modelo_tela import get_telas_collection
from bson import ObjectId
from datetime import datetime
from collections import defaultdict
import uuid

# ---------------------------
# 📌 Crear definición de tela
# ---------------------------
def crear_tela():
    data = request.get_json()
    nombre = data.get("nombre")
    categoria_tela = data.get("categoria_tela")
    relacion_catg_prod = data.get("relacion_catg_prod", [])

    if not nombre or not categoria_tela:
        return jsonify({"ok": False, "msg": "Nombre y categoría son obligatorios"}), 400

    col = get_telas_collection()
    fecha = datetime.utcnow().strftime("%Y-%m")
    codigo = f"{str(categoria_tela)[:3].upper()}-{nombre.upper().replace(' ', '')[:10]}-{fecha}"

    nueva_tela = {
        "codigo_tela": codigo,
        "nombre": nombre,
        "categoria_tela": ObjectId(categoria_tela),
        "estado": "activo",
        "relacion_catg_prod": [ObjectId(r) for r in relacion_catg_prod],
        "lotes": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    result = col.insert_one(nueva_tela)
    nueva_tela["_id"] = str(result.inserted_id)
    nueva_tela["categoria_tela"] = str(nueva_tela["categoria_tela"])
    nueva_tela["relacion_catg_prod"] = [str(r) for r in nueva_tela["relacion_catg_prod"]]

    return jsonify({"ok": True, "msg": "Tela creada", "tela": nueva_tela})


# ---------------------------
# 📌 Listar todas las telas
# ---------------------------
def listar_telas():
    col = get_telas_collection()
    lista = list(col.find({}))
    for t in lista:
        t["_id"] = str(t["_id"])
        t["categoria_tela"] = str(t["categoria_tela"])
        t["relacion_catg_prod"] = [str(r) for r in t.get("relacion_catg_prod", [])]
        for lote in t.get("lotes", []):
            lote["lote_id"] = str(lote["lote_id"])
            if isinstance(lote.get("fecha_compra"), datetime):
                lote["fecha_compra"] = lote["fecha_compra"].strftime("%Y-%m-%d")
            if isinstance(lote.get("created_at"), datetime):
                lote["created_at"] = lote["created_at"].isoformat()
    return jsonify(lista)


# ---------------------------
# 📌 Obtener una tela
# ---------------------------
def obtener_tela(id):
    col = get_telas_collection()
    tela = col.find_one({"_id": ObjectId(id)})
    if not tela:
        return jsonify({"ok": False, "msg": "Tela no encontrada"}), 404

    tela["_id"] = str(tela["_id"])
    tela["categoria_tela"] = str(tela["categoria_tela"])
    tela["relacion_catg_prod"] = [str(r) for r in tela.get("relacion_catg_prod", [])]
    for lote in tela.get("lotes", []):
        lote["lote_id"] = str(lote["lote_id"])
        if isinstance(lote.get("fecha_compra"), datetime):
            lote["fecha_compra"] = lote["fecha_compra"].strftime("%Y-%m-%d")
        if isinstance(lote.get("created_at"), datetime):
            lote["created_at"] = lote["created_at"].isoformat()

    return jsonify(tela)


# ---------------------------
# 📌 Agregar lote a tela
# ---------------------------
def agregar_lote(id):
    data = request.get_json()
    color = data.get("color")
    cantidad = data.get("cantidad")
    precio_unitario = data.get("precio_unitario")
    fecha_compra = data.get("fecha_compra", datetime.utcnow().strftime("%Y-%m-%d"))

    if not color or not cantidad or not precio_unitario:
        return jsonify({"ok": False, "msg": "Datos de lote incompletos"}), 400

    lote = {
        "lote_id": str(uuid.uuid4()),  # 🔹 ahora siempre string
        "color": color,
        "cantidad": float(cantidad),
        "precio_unitario": float(precio_unitario),
        "fecha_compra": fecha_compra,
        "created_at": datetime.utcnow()
    }

    col = get_telas_collection()
    result = col.update_one(
        {"_id": ObjectId(id)},
        {"$push": {"lotes": lote}, "$set": {"updated_at": datetime.utcnow()}}
    )

    if result.modified_count:
        return jsonify({"ok": True, "msg": "Lote agregado", "lote": lote})
    return jsonify({"ok": False, "msg": "Error al agregar lote"}), 400

# ---------------------------
# 📌 Actualizar Tela
# ---------------------------
def actualizar_tela(id):
    data = request.get_json()
    nombre = data.get("nombre")
    categoria_tela = data.get("categoria_tela")
    estado = data.get("estado", "activo")
    relacion_catg_prod = data.get("relacion_catg_prod", [])

    if not nombre or not categoria_tela:
        return jsonify({"ok": False, "msg": "Nombre y categoría son obligatorios"}), 400

    col = get_telas_collection()
    result = col.update_one(
        {"_id": ObjectId(id)},
        {
            "$set": {
                "nombre": nombre,
                "categoria_tela": ObjectId(categoria_tela),
                "estado": estado,
                "relacion_catg_prod": [ObjectId(r) for r in relacion_catg_prod],
                "updated_at": datetime.utcnow()
            }
        }
    )

    if result.modified_count:
        return jsonify({"ok": True, "msg": "Tela actualizada"})
    else:
        return jsonify({"ok": False, "msg": "No se pudo actualizar o no hubo cambios"}), 400



from bson import ObjectId

# ---------------------------
# 📌 Actualizar datos de un lote
# ---------------------------
def actualizar_lote(id, lote_id):
    try:
        data = request.get_json()
        ### print(f"[DEBUG] Datos recibidos para actualizar lote: {data}")

        campos = {}

        if "color" in data and data["color"]:
            campos["lotes.$.color"] = data["color"]

        if "cantidad" in data and data["cantidad"] not in ("", None):
            try:
                campos["lotes.$.cantidad"] = float(data["cantidad"])
            except ValueError:
                return jsonify({"ok": False, "msg": "Cantidad inválida"}), 400

        if "precio_unitario" in data and data["precio_unitario"] not in ("", None):
            try:
                campos["lotes.$.precio_unitario"] = float(data["precio_unitario"])
            except ValueError:
                return jsonify({"ok": False, "msg": "Precio inválido"}), 400

        if "fecha_compra" in data and data["fecha_compra"]:
            campos["lotes.$.fecha_compra"] = data["fecha_compra"]

        campos["lotes.$.updated_at"] = datetime.utcnow()

        if not campos:
            return jsonify({"ok": False, "msg": "No hay datos válidos para actualizar"}), 400

        col = get_telas_collection()

        # 🔹 Intentar actualizar por string
        result = col.update_one(
            {"_id": ObjectId(id), "lotes.lote_id": lote_id},
            {"$set": campos}
        )

        # 🔹 Si no encontró nada, intentar por ObjectId
        if result.modified_count == 0:
            try:
                result = col.update_one(
                    {"_id": ObjectId(id), "lotes.lote_id": ObjectId(lote_id)},
                    {"$set": campos}
                )
            except:
                pass

        if result.modified_count:
            return jsonify({"ok": True, "msg": "Lote actualizado"})
        else:
            return jsonify({"ok": False, "msg": "No se encontró el lote o no hubo cambios"}), 400

    except Exception as e:
        print(f"[ERROR] actualizar_lote: {str(e)}")
        return jsonify({"ok": False, "msg": f"Error interno: {str(e)}"}), 500


# ---------------------------
# 📌 Eliminar un lote de una tela
# ---------------------------
def eliminar_lote(id, lote_id):
    col = get_telas_collection()
    result = col.update_one(
        {"_id": ObjectId(id)},
        {"$pull": {"lotes": {"lote_id": str(lote_id)}}}
    )
    if result.modified_count:
        return jsonify({"ok": True, "msg": "Lote eliminado correctamente"})
    return jsonify({"ok": False, "msg": "No se pudo eliminar el lote"}), 400




# ---------------------------
# 📌 Consumir stock de un lote específico
# ---------------------------
def consumir_lote_especifico(id, lote_id):
    data = request.get_json()
    cantidad_usar = float(data.get("cantidad", 0))

    if cantidad_usar <= 0:
        return jsonify({"ok": False, "msg": "Cantidad inválida"}), 400

    col = get_telas_collection()
    tela = col.find_one({"_id": ObjectId(id)})
    if not tela:
        return jsonify({"ok": False, "msg": "Tela no encontrada"}), 404

    lote = next((l for l in tela.get("lotes", []) if str(l["lote_id"]) == lote_id), None)
    if not lote:
        return jsonify({"ok": False, "msg": "Lote no encontrado"}), 404

    if lote["cantidad"] < cantidad_usar:
        return jsonify({"ok": False, "msg": "Stock insuficiente en este lote"}), 400

    col.update_one(
        {"_id": ObjectId(id), "lotes.lote_id": lote_id},
        {"$inc": {"lotes.$.cantidad": -cantidad_usar}, "$set": {"updated_at": datetime.utcnow()}}
    )
    return jsonify({"ok": True, "msg": f"Se consumió {cantidad_usar}m del lote {lote_id}."})


# ---------------------------
# 📌 Consumir stock por color
# ---------------------------
def consumir_lote_color(id):
    data = request.get_json()
    color = data.get("color")
    cantidad = float(data.get("cantidad", 0))

    if not color or cantidad <= 0:
        return jsonify({"ok": False, "msg": "Color y cantidad son obligatorios"}), 400

    col = get_telas_collection()
    tela = col.find_one({"_id": ObjectId(id)})
    if not tela:
        return jsonify({"ok": False, "msg": "Tela no encontrada"}), 404

    stock_disponible = sum(
        float(lote.get("cantidad", 0))
        for lote in tela.get("lotes", [])
        if lote.get("color", "").lower() == color.lower()
    )
    if stock_disponible < cantidad:
        return jsonify({
            "ok": False,
            "msg": f"Stock insuficiente de {color}",
            "stock_disponible": stock_disponible,
            "cantidad_solicitada": cantidad
        }), 400

    for lote in tela["lotes"]:
        if lote.get("color", "").lower() == color.lower() and cantidad > 0:
            disponible = float(lote.get("cantidad", 0))
            if disponible >= cantidad:
                lote["cantidad"] = disponible - cantidad
                cantidad = 0
            else:
                lote["cantidad"] = 0
                cantidad -= disponible

    col.update_one({"_id": ObjectId(id)}, {"$set": {"lotes": tela["lotes"], "updated_at": datetime.utcnow()}})
    return jsonify({"ok": True, "msg": f"Se descontó correctamente {data.get('cantidad')} metros de {color}."})


# ---------------------------
# 📌 Eliminar tela
# ---------------------------
def eliminar_tela(id):
    col = get_telas_collection()
    result = col.delete_one({"_id": ObjectId(id)})
    if result.deleted_count:
        return jsonify({"ok": True, "msg": "Tela eliminada"})
    else:
        return jsonify({"ok": False, "msg": "No encontrada"}), 404


# ---------------------------
# 📌 Obtener stock total por color
# ---------------------------
def stock_tela(id):
    col = get_telas_collection()
    tela = col.find_one({"_id": ObjectId(id)})

    if not tela:
        return jsonify({"ok": False, "msg": "Tela no encontrada"}), 404

    resumen_colores = defaultdict(float)
    stock_total = 0.0

    for lote in tela.get("lotes", []):
        color = lote.get("color", "Desconocido")
        cantidad = float(lote.get("cantidad", 0))
        resumen_colores[color] += cantidad
        stock_total += cantidad

    return jsonify({
        "ok": True,
        "tela_id": str(tela["_id"]),
        "nombre": tela["nombre"],
        "stock_por_color": [
            {"color": c, "cantidad_total": cant}
            for c, cant in resumen_colores.items()
        ],
        "stock_total": stock_total
    })


# ---------------------------
# 📌 Validar stock de un color específico
# ---------------------------
def validar_stock(id):
    data = request.get_json()
    color = data.get("color")
    cantidad_necesaria = float(data.get("cantidad", 0))

    if not color or cantidad_necesaria <= 0:
        return jsonify({"ok": False, "msg": "Color y cantidad son obligatorios"}), 400

    col = get_telas_collection()
    tela = col.find_one({"_id": ObjectId(id)})

    if not tela:
        return jsonify({"ok": False, "msg": "Tela no encontrada"}), 404

    stock_disponible = sum(
        float(lote.get("cantidad", 0))
        for lote in tela.get("lotes", [])
        if lote.get("color", "").lower() == color.lower()
    )

    if stock_disponible >= cantidad_necesaria:
        return jsonify({
            "ok": True,
            "msg": f"Stock suficiente de {color}",
            "stock_disponible": stock_disponible,
            "cantidad_solicitada": cantidad_necesaria
        })
    else:
        return jsonify({
            "ok": False,
            "msg": f"Stock insuficiente de {color}",
            "stock_disponible": stock_disponible,
            "cantidad_solicitada": cantidad_necesaria
        }), 400



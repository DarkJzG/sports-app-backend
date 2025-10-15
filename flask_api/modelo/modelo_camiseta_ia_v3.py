# flask_api/modelo/modelo_camiseta_ia_v3.py
from flask import current_app
from bson import ObjectId

def guardar_camiseta_ia_v3(user_id, categoria_id, atributos, image_url, prompt):
    db = current_app.db
    doc = {
        "user_id": ObjectId(user_id) if user_id else None,
        "categoria_id": categoria_id,
        "diseno": atributos.get("diseno"),
        "atributos": atributos,
        "prompt": prompt,
        "image_url": image_url,
        "fecha": current_app.timezone.now().isoformat(),
    }
    result = db.camisetas_ia_v3.insert_one(doc)
    return str(result.inserted_id)

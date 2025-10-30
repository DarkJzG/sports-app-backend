# flask_api/modelo/modelo_empresa.py
from flask import current_app
from bson import ObjectId
from datetime import datetime, timezone


def get_empresa_collection():
    """Obtiene la colección de empresa"""
    return current_app.mongo.db.empresa


def _now_utc():
    """Retorna la fecha/hora actual en UTC"""
    return datetime.now(timezone.utc)


def _to_iso(dt):
    """Convierte datetime a formato ISO string"""
    try:
        return dt.isoformat().replace("+00:00", "Z")
    except Exception:
        return dt


def _serialize(doc: dict) -> dict:
    """Serializa un documento de empresa"""
    if not doc:
        return None
    
    doc["_id"] = str(doc["_id"])
    
    # Serializar fechas
    if "createdAt" in doc:
        doc["createdAt"] = _to_iso(doc["createdAt"])
    if "updatedAt" in doc:
        doc["updatedAt"] = _to_iso(doc["updatedAt"])
    
    return doc


def obtener_empresa():
    """
    Obtiene la información de la empresa.
    Solo puede haber un registro de empresa.
    """
    col = get_empresa_collection()
    empresa = col.find_one()
    
    if not empresa:
        # Si no existe, crear un registro por defecto
        empresa_default = {
            "nombre": "Tu Empresa S.A.",
            "ruc": "1234567890001",
            "direccion": "Calle Principal #123",
            "ciudad": "Ciudad",
            "provincia": "Provincia",
            "pais": "Ecuador",
            "telefono": "(593) 2-123-4567",
            "celular": "0999999999",
            "email": "ventas@tuempresa.com",
            "sitioWeb": "www.tuempresa.com",
            "descripcion": "Empresa dedicada a...",
            "logo": "",
            "banner": "",
            "favicon": "",
            "imagenPdf": "",
            "redesSociales": {
                "facebook": "",
                "instagram": "",
                "twitter": "",
                "whatsapp": "",
                "tiktok": ""
            },
            "datosBancarios": {
                "banco": "Banco del País",
                "tipoCuenta": "Corriente",
                "numeroCuenta": "1234567890",
                "titular": "Tu Empresa S.A."
            },
            "horarioAtencion": {
                "lunes": "08:00 - 18:00",
                "martes": "08:00 - 18:00",
                "miercoles": "08:00 - 18:00",
                "jueves": "08:00 - 18:00",
                "viernes": "08:00 - 18:00",
                "sabado": "09:00 - 14:00",
                "domingo": "Cerrado"
            },
            "configuracion": {
                "iva": 15,
                "moneda": "USD",
                "simboloMoneda": "$"
            },
            "createdAt": _now_utc(),
            "updatedAt": _now_utc()
        }
        result = col.insert_one(empresa_default)
        empresa = col.find_one({"_id": result.inserted_id})
    
    return _serialize(empresa)


def actualizar_empresa(data: dict):
    """
    Actualiza la información de la empresa.
    """
    col = get_empresa_collection()
    empresa = col.find_one()
    
    if not empresa:
        # Si no existe, crear el registro
        obtener_empresa()
        empresa = col.find_one()
    
    # Preparar datos de actualización
    update_data = {
        "updatedAt": _now_utc()
    }
    
    # Campos simples
    campos_simples = [
        "nombre", "ruc", "direccion", "ciudad", "provincia", "pais",
        "telefono", "celular", "email", "sitioWeb", "descripcion",
        "logo", "banner", "favicon", "imagenPdf"
    ]
    
    for campo in campos_simples:
        if campo in data:
            update_data[campo] = data[campo]
    
    # Campos complejos
    if "redesSociales" in data:
        update_data["redesSociales"] = data["redesSociales"]
    
    if "datosBancarios" in data:
        update_data["datosBancarios"] = data["datosBancarios"]
    
    if "horarioAtencion" in data:
        update_data["horarioAtencion"] = data["horarioAtencion"]
    
    if "configuracion" in data:
        update_data["configuracion"] = data["configuracion"]
    
    # Actualizar
    result = col.update_one(
        {"_id": empresa["_id"]},
        {"$set": update_data}
    )
    
    if result.modified_count > 0 or result.matched_count > 0:
        empresa_actualizada = col.find_one({"_id": empresa["_id"]})
        return _serialize(empresa_actualizada)
    
    return None


def subir_imagen_empresa(campo: str, url: str):
    """
    Actualiza una imagen específica de la empresa.
    
    Args:
        campo: 'logo', 'banner', 'favicon', o 'imagenPdf'
        url: URL de Cloudinary de la imagen
    """
    col = get_empresa_collection()
    empresa = col.find_one()
    
    if not empresa:
        obtener_empresa()
        empresa = col.find_one()
    
    campos_validos = ["logo", "banner", "favicon", "imagenPdf"]
    if campo not in campos_validos:
        return None
    
    result = col.update_one(
        {"_id": empresa["_id"]},
        {
            "$set": {
                campo: url,
                "updatedAt": _now_utc()
            }
        }
    )
    
    if result.modified_count > 0 or result.matched_count > 0:
        empresa_actualizada = col.find_one({"_id": empresa["_id"]})
        return _serialize(empresa_actualizada)
    
    return None

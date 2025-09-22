# flask_api/rutas/ruta_producto.py

from flask import Blueprint
from flask_api.controlador import control_producto

producto_bp = Blueprint("producto", __name__, url_prefix="/producto")

@producto_bp.route("/add", methods=["POST"])
def add_producto():
    return control_producto.crear_producto()

@producto_bp.route("/all", methods=["GET"])
def all_productos():
    return control_producto.listar_productos()

@producto_bp.route("/get/<id>", methods=["GET"])
def get_producto(id):
    return control_producto.obtener_producto(id)

@producto_bp.route("/update/<id>", methods=["PUT"])
def update_producto(id):
    return control_producto.actualizar_producto(id)

@producto_bp.route("/delete/<id>", methods=["DELETE"])
def delete_producto(id):
    return control_producto.eliminar_producto(id)

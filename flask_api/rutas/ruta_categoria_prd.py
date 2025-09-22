# flask_api/rutas/ruta_categoria_prd.py
from flask import Blueprint
from flask_api.controlador import control_categoria_prd

catg_prod_bp = Blueprint("catg_prod", __name__, url_prefix="/catg_prod")

# ---------------------------
# 📌 CRUD Categoría Producto
# ---------------------------

@catg_prod_bp.route("/add", methods=["POST"])
def add_categoria():
    return control_categoria_prd.crear_categoria()


@catg_prod_bp.route("/all", methods=["GET"])
def get_categorias():
    return control_categoria_prd.listar_categorias()


@catg_prod_bp.route("/get/<id>", methods=["GET"])
def get_categoria(id):
    return control_categoria_prd.obtener_categoria(id)


@catg_prod_bp.route("/update/<id>", methods=["PUT"])
def update_categoria(id):
    return control_categoria_prd.actualizar_categoria(id)


@catg_prod_bp.route("/delete/<id>", methods=["DELETE"])
def delete_categoria(id):
    return control_categoria_prd.eliminar_categoria(id)

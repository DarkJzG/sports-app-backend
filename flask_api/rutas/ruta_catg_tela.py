# flask_api/rutas/ruta_catg_tela.py
from flask import Blueprint
from flask_api.controlador import control_catg_tela

catg_tela_bp = Blueprint("catg_tela", __name__, url_prefix="/catg_tela")

@catg_tela_bp.route("/add", methods=["POST"])
def add_catg_tela():
    return control_catg_tela.crear_catg_tela()

@catg_tela_bp.route("/all", methods=["GET"])
def all_catg_telas():
    return control_catg_tela.listar_catg_telas()

@catg_tela_bp.route("/get/<id>", methods=["GET"])
def get_catg_tela(id):
    return control_catg_tela.obtener_catg_tela(id)

@catg_tela_bp.route("/update/<id>", methods=["PUT"])
def update_catg_tela(id):
    return control_catg_tela.actualizar_catg_tela(id)

@catg_tela_bp.route("/delete/<id>", methods=["DELETE"])
def delete_catg_tela(id):
    return control_catg_tela.eliminar_catg_tela(id)

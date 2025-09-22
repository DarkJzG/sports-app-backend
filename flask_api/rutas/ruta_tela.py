# flask_api/rutas/ruta_tela.py
from flask import Blueprint
from flask_api.controlador import control_tela

tela_bp = Blueprint("tela", __name__, url_prefix="/tela")

# ---------------------------
# 📌 CRUD Tela
# ---------------------------
@tela_bp.route("/add", methods=["POST"])
def add_tela():
    return control_tela.crear_tela()

@tela_bp.route("/all", methods=["GET"])
def all_telas():
    return control_tela.listar_telas()

@tela_bp.route("/get/<id>", methods=["GET"])
def get_tela(id):
    return control_tela.obtener_tela(id)

@tela_bp.route("/delete/<id>", methods=["DELETE"])
def delete_tela(id):
    return control_tela.eliminar_tela(id)

@tela_bp.route("/update/<id>", methods=["PUT"])
def update_tela(id):
    return control_tela.actualizar_tela(id)



# ---------------------------
# 📌 Gestión de Lotes
# ---------------------------
@tela_bp.route("/add_lote/<id>", methods=["POST"])
def add_lote(id):
    return control_tela.agregar_lote(id)

@tela_bp.route("/update_lote/<id>/<lote_id>", methods=["PUT"])
def update_lote(id, lote_id):
    return control_tela.actualizar_lote(id, lote_id)

@tela_bp.route("/delete_lote/<id>/<lote_id>", methods=["DELETE"])
def delete_lote(id, lote_id):
    return control_tela.eliminar_lote(id, lote_id)

@tela_bp.route("/consumir_lote_especifico/<id>/<lote_id>", methods=["POST"])
def consumir_lote_especifico(id, lote_id):
    return control_tela.consumir_lote_especifico(id, lote_id)

@tela_bp.route("/consumir_lote_color/<id>", methods=["POST"])
def consumir_lote_color(id):
    return control_tela.consumir_lote_color(id)


# ---------------------------
# 📌 Stock
# ---------------------------
@tela_bp.route("/stock/<id>", methods=["GET"])
def stock_tela(id):
    return control_tela.stock_tela(id)

@tela_bp.route("/validar_stock/<id>", methods=["POST"])
def validar_stock(id):
    return control_tela.validar_stock(id)

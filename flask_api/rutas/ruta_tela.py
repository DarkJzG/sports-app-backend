# flask_api/rutas/ruta_tela.py

from flask import Blueprint
from flask_api.controlador import control_tela

tela_bp = Blueprint('tela', __name__, url_prefix='/tela')

@tela_bp.route('/add', methods=['POST'])
def add_tela():
    return control_tela.crear_tela()

@tela_bp.route('/all', methods=['GET'])
def all_telas():
    return control_tela.listar_telas()

@tela_bp.route('/get/<id>', methods=['GET'])
def get_tela(id):
    return control_tela.obtener_tela(id)

@tela_bp.route('/update/<id>', methods=['PUT'])
def update_tela(id):
    return control_tela.actualizar_tela(id)

@tela_bp.route('/delete/<id>', methods=['DELETE'])
def delete_tela(id):
    return control_tela.eliminar_tela(id)

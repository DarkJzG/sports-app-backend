# flask_api/rutas/ruta_mano_obra.py

from flask import Blueprint, request
from flask_api.controlador import control_mano_obra

mano_bp = Blueprint('mano', __name__, url_prefix='/mano')

@mano_bp.route('/add', methods=['POST'])
def add_mano():
    return control_mano_obra.crear_mano_obra()

@mano_bp.route('/all', methods=['GET'])
def all_mano():
    return control_mano_obra.listar_mano_obra()

@mano_bp.route('/get/<id>', methods=['GET'])
def get_mano(id):
    return control_mano_obra.obtener_mano_obra(id)

@mano_bp.route('/update/<id>', methods=['PUT'])
def update_mano(id):
    return control_mano_obra.actualizar_mano_obra(id)

@mano_bp.route('/delete/<id>', methods=['DELETE'])
def delete_mano(id):
    return control_mano_obra.eliminar_mano_obra(id)

from werkzeug.security import check_password_hash
from flask import jsonify
from flask_api.modelo.modelo_usuario import get_users_collection

def login_user(data):
    correo = data.get('correo')
    password = data.get('password')
    if not correo or not password:
        return jsonify({'ok': False, 'msg': 'Datos incompletos'}), 400

    users = get_users_collection()
    user = users.find_one({'correo': correo})

    if user and check_password_hash(user['password'], password):
        return jsonify({
            'ok': True,
            'msg': 'Inicio de sesión exitoso',
            'usuario': {
                'id': str(user['_id']),
                'nombre': user['nombre'],
                'correo': user['correo'],
                'rol': user.get('rol', 'cliente')
            }
        })
    else:
        return jsonify({'ok': False, 'msg': 'Correo o contraseña incorrectos'}), 401

from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from werkzeug.security import generate_password_hash

app = Flask(__name__)
CORS(app)

# Conexión a tu base de datos sportsapp
app.config["MONGO_URI"] = "mongodb+srv://1djohanburbano:6rsVRkmjkrmWv4Ic@cluster0.vujwwmh.mongodb.net/sportsapp?retryWrites=true&w=majority&appName=Cluster0"
mongo = PyMongo(app)

@app.route('/')
def home():
    return "¡Flask API corriendo correctamente!"

@app.route('/test_mongo')
def test_mongo():
    try:
        colls = mongo.db.list_collection_names()
        return jsonify({"ok": True, "collections": colls})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    nombre = data.get('nombre')
    correo = data.get('correo')
    password = data.get('password')

    if not nombre or not correo or not password:
        return jsonify({'ok': False, 'msg': 'Datos incompletos'}), 400

    users = mongo.db.users
    if users.find_one({'correo': correo}):
        return jsonify({'ok': False, 'msg': 'El correo ya está registrado'}), 400

    hashed_pw = generate_password_hash(password)
    user = {
        'nombre': nombre,
        'correo': correo,
        'password': hashed_pw
    }
    users.insert_one(user)
    return jsonify({'ok': True, 'msg': 'Usuario registrado con éxito'}), 201

if __name__ == '__main__':
    app.run(debug=True)

# flask_api/app.py
from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_api.config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
mongo = PyMongo(app)
app.mongo = mongo


from flask_api.rutas.ruta_registro import registro_bp
from flask_api.rutas.ruta_login import login_bp
from flask_api.rutas.ruta_categoria_prd import catg_bp

from flask_api.rutas.ruta_mano_obra import mano_bp
from flask_api.rutas.ruta_tela import tela_bp
from flask_api.rutas.ruta_producto import producto_bp

app.register_blueprint(registro_bp)
app.register_blueprint(login_bp)
app.register_blueprint(catg_bp)
app.register_blueprint(mano_bp)
app.register_blueprint(tela_bp)
app.register_blueprint(producto_bp)

@app.route("/")
def home():
    return "¡API corriendo correctamente!"

if __name__ == "__main__":
    app.run(debug=True)

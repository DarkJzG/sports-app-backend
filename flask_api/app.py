# flask_api/app.py
import os

from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from pymongo import MongoClient
from flask_api.config import Config
from flask_api.extensiones import mail

from flask_api.rutas.ruta_registro import registro_bp
from flask_api.rutas.ruta_login import login_bp
from flask_api.rutas.ruta_categoria_prd import catg_bp

from flask_api.rutas.ruta_mano_obra import mano_bp
from flask_api.rutas.ruta_tela import tela_bp
from flask_api.rutas.ruta_producto import producto_bp

from flask_api.rutas.ruta_carrito import carrito_bp

from flask_api.rutas.ruta_ia import ruta_ia

app = Flask(__name__)


mongo_uri = os.getenv("MONGO_URI")
print(f"Conectando a MongoDB con URI: {mongo_uri}")

client = MongoClient(mongo_uri)
db = client["sportsapp"]

try:
    client.admin.command("ping")
    print("✅ Conexión a MongoDB exitosa")
except Exception as e:
    print("❌ Error conectando a MongoDB:", e)

app.config.from_object(Config)



CORS(app, 
     resources={r"/*": {"origins": [
        "http://localhost:3000",
        "http://192.168.3.241:3000"
    ]}}, 
    supports_credentials=True)

mail.init_app(app)
mongo = PyMongo(app)
app.mongo = mongo




app.register_blueprint(registro_bp)
app.register_blueprint(login_bp)
app.register_blueprint(catg_bp)
app.register_blueprint(mano_bp)
app.register_blueprint(tela_bp)
app.register_blueprint(producto_bp)
app.register_blueprint(carrito_bp)
app.register_blueprint(ruta_ia)

@app.route("/")
def home():
    return "¡API corriendo correctamente!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

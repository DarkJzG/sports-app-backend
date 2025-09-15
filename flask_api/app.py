# flask_api/app.py
import os
import cloudinary
import cloudinary.uploader

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
from flask_api.rutas.ruta_ia_stabledf import ruta_ia_stable
from flask_api.rutas.ruta_ia_prendas import ruta_ia_prendas

from flask_api.rutas.ruta_prendas_ia import prendas_ia_bp


app = Flask(__name__)
app.config.from_object(Config)

mongo_uri = os.getenv("MONGO_URI")
print(f"Conectando a MongoDB con URI: {mongo_uri}")


client = MongoClient(mongo_uri)
db = client["sportsapp"]

try:
    client.admin.command("ping")
    print("✅ Conexión a MongoDB exitosa")
except Exception as e:
    print("❌ Error conectando a MongoDB:", e)

mongo = PyMongo(app)
app.mongo = mongo

cloudinary.config(
    cloud_name=app.config["CLOUDINARY_CLOUD_NAME"],
    api_key=app.config["CLOUDINARY_API_KEY"],
    api_secret=app.config["CLOUDINARY_API_SECRET"]
)

CORS(app, 
     resources={r"/*": {"origins": [
        "http://localhost:3000",
        "http://192.168.3.241:3000"
    ]}}, 
    supports_credentials=True)


mail.init_app(app)





app.register_blueprint(registro_bp)
app.register_blueprint(login_bp)
app.register_blueprint(catg_bp)
app.register_blueprint(mano_bp)
app.register_blueprint(tela_bp)
app.register_blueprint(producto_bp)
app.register_blueprint(carrito_bp)
app.register_blueprint(ruta_ia)
app.register_blueprint(ruta_ia_stable)
app.register_blueprint(ruta_ia_prendas)
app.register_blueprint(prendas_ia_bp)

@app.route("/")
def home():
    return "¡API corriendo correctamente!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

# flask_api/app.py
import os
import cloudinary
import cloudinary.uploader
import google.generativeai as genai

from flask import jsonify
from dotenv import load_dotenv

load_dotenv()

from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from pymongo import MongoClient
from flask_api.config import Config
from flask_api.extensiones import mail
from flask_jwt_extended import JWTManager

from flask_api.rutas.ruta_empresa import empresa_bp

from flask_api.rutas.ruta_autenticacion import auth_bp
from flask_api.rutas.ruta_usuario import usuario_bp


from flask_api.rutas.ruta_categoria_prd import catg_prod_bp
from flask_api.rutas.ruta_catg_tela import catg_tela_bp

from flask_api.rutas.ruta_mano_obra import mano_bp
from flask_api.rutas.ruta_tela import tela_bp

from flask_api.rutas.ruta_producto import producto_bp

from flask_api.rutas.ruta_carrito import carrito_bp
from flask_api.rutas.ruta_pedido import pedido_bp


##Pruebas de IA
from flask_api.rutas.ruta_ia import ruta_ia
from flask_api.rutas.ruta_ia_stabledf import ruta_ia_stable
from flask_api.rutas.ruta_ia_prendas import ruta_ia_prendas

from flask_api.rutas.ruta_prendas_ia import prendas_ia_bp
from flask_api.rutas.ruta_ia_texturas import ruta_ia_texturas

from flask_api.rutas.ruta_camiseta_ia import ruta_camiseta_ia
from flask_api.rutas.ruta_ia_camiseta import ruta_ia_camiseta
from flask_api.rutas.ruta_camiseta_ia_v3 import ruta_camiseta_ia_v3

from flask_api.rutas.ruta_ficha_tecnica import ruta_ficha_tecnica
from flask_api.rutas.ruta_3d_prenda import ruta_3d_prenda
from flask_api.rutas.ruta_3d_logos import ruta_3d_logos
from flask_api.rutas.ruta_pedido_ficha import ruta_pedido_ficha

from flask_api.rutas.ruta_camiseta_gemini_v3 import ruta_camiseta_gemini_v3
from flask_api.rutas.ruta_chompa_ia_v1 import ruta_chompa_ia_v1
from flask_api.rutas.ruta_pantalon_ia_v1 import ruta_pantalon_ia_v1
from flask_api.rutas.ruta_conjunto_externo_ia_v1 import ruta_conjunto_externo_ia_v1
from flask_api.rutas.ruta_pantaloneta_ia_v1 import ruta_pantaloneta_ia_v1
from flask_api.rutas.ruta_prompts import ruta_prompts
from flask_api.rutas.ruta_prendas_huggingface import ruta_prendas_hf


app = Flask(__name__)
app.config.from_object(Config)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024


mongo_uri = os.getenv("MONGO_URI")
print(f"Conectando a MongoDB con URI: {mongo_uri}")
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
    print("Gemini API configurada exitosamente.")
else:
    print("ADVERTENCIA: GEMINI_API_KEY no encontrada.")

jwt = JWTManager(app)
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
app.config["JWT_ERROR_MESSAGE_KEY"] = "msg"
app.config["FRONTEND_URL"] = "http://localhost:3000"





client = MongoClient(mongo_uri)
db = client["sportsapp"]

try:
    client.admin.command("ping")
    print("Conexión a MongoDB exitosa")
    print("FRONTEND_URL en app:", app.config["FRONTEND_URL"])

except Exception as e:
    print(" Error conectando a MongoDB:", e)

mongo = PyMongo(app)
app.mongo = mongo

cloudinary.config(
    cloud_name=app.config["CLOUDINARY_CLOUD_NAME"],
    api_key=app.config["CLOUDINARY_API_KEY"],
    api_secret=app.config["CLOUDINARY_API_SECRET"]
)

CORS(app, 
     resources={r"/*": {
        "origins": [
            "http://localhost:3000",
            "http://192.168.3.241:3000"
        ],
        "methods": ["GET", "POST", "PUT","PATCH", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Authorization"]

    }}, 
    supports_credentials=True)


mail.init_app(app)


app.register_blueprint(empresa_bp)

app.register_blueprint(auth_bp)
app.register_blueprint(usuario_bp)

app.register_blueprint(catg_prod_bp)
app.register_blueprint(catg_tela_bp)
app.register_blueprint(mano_bp)
app.register_blueprint(tela_bp)
app.register_blueprint(producto_bp)

app.register_blueprint(carrito_bp)
app.register_blueprint(pedido_bp)

app.register_blueprint(ruta_ia)
app.register_blueprint(ruta_ia_stable)
app.register_blueprint(ruta_ia_prendas)
app.register_blueprint(prendas_ia_bp)
app.register_blueprint(ruta_ia_texturas)
app.register_blueprint(ruta_camiseta_ia)
app.register_blueprint(ruta_ia_camiseta)
app.register_blueprint(ruta_camiseta_ia_v3)
app.register_blueprint(ruta_ficha_tecnica)
app.register_blueprint(ruta_3d_prenda)
app.register_blueprint(ruta_3d_logos)
app.register_blueprint(ruta_pedido_ficha)

app.register_blueprint(ruta_camiseta_gemini_v3)
app.register_blueprint(ruta_chompa_ia_v1)
app.register_blueprint(ruta_pantalon_ia_v1)
app.register_blueprint(ruta_conjunto_externo_ia_v1)
app.register_blueprint(ruta_pantaloneta_ia_v1)
app.register_blueprint(ruta_prompts)

app.register_blueprint(ruta_prendas_hf)

@app.route("/")
def home():
    return "¡API corriendo correctamente!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

@app.errorhandler(Exception)
def handle_error(e):
    print(" Error general:", e)
    return jsonify({"ok": False, "msg": str(e)}), 500
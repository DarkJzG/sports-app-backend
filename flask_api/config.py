# flask_api/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:

    #URL FRONTEND
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Mongo
    MONGO_URI = os.getenv("MONGO_URI")

    #Stable Diffusion
    STABLE_URL = os.getenv("STABLE_URL", "http://127.0.0.1:7860")

    # Cloudinary
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "dcn5d4wbo")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "233547317788382")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "_Y_acHO10geJ7Z8Nape29CDPOdA")

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "Tupapitochulo_69")


    # Mail
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = (
        os.getenv("MAIL_DEFAULT_SENDER_NAME", "Johan Sports"),
        os.getenv("MAIL_DEFAULT_SENDER_EMAIL", os.getenv("MAIL_USERNAME", "HOLA MI GENTE DE YOUTUBE")),
    )

    # Replicate
    REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
    REPLICATE_MODEL = os.getenv("REPLICATE_MODEL", "stability-ai/sdxl")
    REPLICATE_VERSION = os.getenv("REPLICATE_VERSION") 

    HORDE_API_KEY = os.getenv("HORDE_API_KEY")
    HORDE_BASE_URL = os.getenv("HORDE_BASE_URL", "https://aihorde.net/api")

import os
from huggingface_hub import InferenceClient
from flask import Flask, request, send_file, jsonify
from io import BytesIO
from flask import Blueprint

ruta_prompts = Blueprint("ruta_prompts", __name__, url_prefix='/api/ia')

# Inicializar el cliente de Hugging Face
client = InferenceClient(
    provider="auto",
    api_key=os.environ["HF_TOKEN"]
)

@ruta_prompts.route('/generar-prenda', methods=['POST'])
def generar_prenda():
    try:
        # Recibir el prompt desde el frontend
        data = request.json
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({"error": "Prompt no proporcionado"}), 400
        
        # Generar la imagen usando Hugging Face
        image = client.text_to_image(
            prompt,
            model="black-forest-labs/FLUX.1-schnell"  # Modelo rápido y gratuito
        )
        
        # Convertir PIL.Image a bytes para enviar al frontend
        img_io = BytesIO()
        image.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

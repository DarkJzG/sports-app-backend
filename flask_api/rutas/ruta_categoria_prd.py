# flask_api/rutas/ruta_categoria_prd.py
from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename

catg_bp = Blueprint('catg', __name__, url_prefix='/catg')

UPLOAD_FOLDER = 'uploads/categorias'  # ruta donde se guardarán imágenes
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@catg_bp.route('/add', methods=['POST'])
def add_categoria():
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    file = request.files.get('imagen')
    if not nombre or not descripcion or not file or not allowed_file(file.filename):
        return jsonify({'ok': False, 'msg': 'Datos incompletos o imagen no permitida'}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file.save(save_path)

    db = current_app.mongo.db
    db.catg_prod.insert_one({
        'nombre': nombre,
        'descripcion': descripcion,
        'imagen_url': f"/{save_path}"
    })
    return jsonify({'ok': True, 'msg': 'Categoría agregada correctamente'})

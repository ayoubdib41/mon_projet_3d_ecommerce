import os
import mimetypes
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS 
from werkzeug.utils import secure_filename
import uuid

# Importer le script de reconstruction
from reconstruct_3d import run_3d_reconstruction 

app = Flask(__name__)
CORS(app) 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
MODELS_FOLDER = os.path.join(BASE_DIR, 'models')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MODELS_FOLDER'] = MODELS_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MODELS_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

@app.route('/')
def index():
    return "L'API de génération 3D est en ligne !"

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        return jsonify({'error': 'Aucun fichier reçu'}), 400
    
    files = request.files.getlist('files[]')
    if not files or len(files) < 2:
        return jsonify({'error': 'Veuillez envoyer au moins 2 images.'}), 400

    session_id = str(uuid.uuid4())
    session_upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    os.makedirs(session_upload_folder, exist_ok=True)

    uploaded_filepaths = []
    for file in files:
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(session_upload_folder, filename)
            file.save(filepath)
            uploaded_filepaths.append(filepath)
    
    product_id = f"product_{str(uuid.uuid4())[:8]}"

    generated_model_filepath = run_3d_reconstruction(
        image_paths=uploaded_filepaths, 
        output_folder=app.config['MODELS_FOLDER'], 
        product_id=product_id
    )

    if generated_model_filepath and os.path.exists(generated_model_filepath):
        model_filename = os.path.basename(generated_model_filepath)
        return jsonify({
            'message': 'Modèle 3D généré avec succès !',
            'model_url': f"/models/{model_filename}"
        }), 200
    else:
        return jsonify({'error': 'Échec de la reconstruction 3D.'}), 500

@app.route('/models/<filename>')
def serve_model(filename):
    response = send_from_directory(app.config['MODELS_FOLDER'], filename)
    if filename.endswith('.glb'):
        response.mimetype = 'model/gltf-binary'
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)
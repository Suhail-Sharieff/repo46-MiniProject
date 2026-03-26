from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import cv2
import api

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/encode', methods=['POST'])
def encode():
    stego_type = request.form.get('type')
    secret_text = request.form.get('text')
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    filename = file.filename
    in_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(in_path)
    
    out_path = os.path.join(UPLOAD_FOLDER, 'stego_' + filename)
    
    try:
        if stego_type == 'image':
            img = cv2.imread(in_path)
            api.encode_img_data(img, secret_text, out_path)
        elif stego_type == 'text':
            api.txt_encode(secret_text, in_path, out_path)
        elif stego_type == 'audio':
            api.encode_aud_data(in_path, secret_text, out_path)
        else:
            return jsonify({'error': 'Invalid stego type'}), 400
            
        return send_file(out_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/decode', methods=['POST'])
def decode():
    stego_type = request.form.get('type')
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
        
    file = request.files['file']
    filename = file.filename
    in_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(in_path)
    
    try:
        if stego_type == 'image':
            img = cv2.imread(in_path)
            decoded = api.decode_img_data(img)
        elif stego_type == 'text':
            decoded = api.decode_txt_data(in_path)
        elif stego_type == 'audio':
            decoded = api.decode_aud_data(in_path)
        else:
            return jsonify({'error': 'Invalid stego type'}), 400
            
        return jsonify({'hidden_text': decoded})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

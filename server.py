from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from flasgger import Swagger, swag_from
import os
import cv2
import api

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/encode', methods=['POST'])
@swag_from({
    'responses': {
        200: {
            'description': 'Returns the encoded stego file or JSON with metrics',
        },
        400: {
            'description': 'Invalid input or missing file'
        }
    },
    'parameters': [
        {
            'name': 'type',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Type of cover file (image, text, audio)'
        },
        {
            'name': 'text',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Secret text to hide'
        },
        {
            'name': 'password',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'Optional password for advanced hybrid AES encryption & PRNG scattering (Images only)'
        },
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'Cover file to hide the text in'
        }
    ]
})
def encode():
    stego_type = request.form.get('type')
    secret_text = request.form.get('text')
    password = request.form.get('password', '')
    
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
            if password:
                # Advanced Mode
                stego_img = api.encode_img_advanced(img, secret_text, password, out_path)
                psnr, ssim_val = api.calculate_metrics(img, stego_img)
                return jsonify({
                    'message': 'Encoding successful',
                    'file_url': f'/uploads/stego_{filename}',
                    'metrics': {
                        'psnr': round(psnr, 2),
                        'ssim': round(ssim_val, 4)
                    }
                })
            else:
                # Basic Mode
                api.encode_img_data(img, secret_text, out_path)
                return send_file(out_path, as_attachment=True)
        elif stego_type == 'text':
            api.txt_encode(secret_text, in_path, out_path)
            return send_file(out_path, as_attachment=True)
        elif stego_type == 'audio':
            api.encode_aud_data(in_path, secret_text, out_path)
            return send_file(out_path, as_attachment=True)
        else:
            return jsonify({'error': 'Invalid stego type'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/decode', methods=['POST'])
@swag_from({
    'responses': {
        200: {
            'description': 'Returns the decoded secret text',
        },
        400: {
            'description': 'Invalid input or missing file'
        }
    },
    'parameters': [
        {
            'name': 'type',
            'in': 'formData',
            'type': 'string',
            'required': True,
            'description': 'Type of stego file (image, text, audio)'
        },
        {
            'name': 'password',
            'in': 'formData',
            'type': 'string',
            'required': False,
            'description': 'Password used during encoding (required if advanced mode was used)'
        },
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'Stego file containing the hidden text'
        }
    ]
})
def decode():
    stego_type = request.form.get('type')
    password = request.form.get('password', '')
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
        
    file = request.files['file']
    filename = file.filename
    in_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(in_path)
    
    try:
        if stego_type == 'image':
            img = cv2.imread(in_path)
            if password:
                decoded = api.decode_img_advanced(img, password)
            else:
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
    app.run(host='0.0.0.0', port=6868)

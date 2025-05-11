from flask import Flask, render_template, request, jsonify
import requests
import os

# Initialize Flask app with explicit template folder
app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect_language', methods=['POST'])
def detect_language():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file'}), 400
    
    audio_file = request.files['audio']
    try:
        response = requests.post(
            'http://whisper:8000/detect',
            files={'audio': audio_file},
            timeout=30
        )
        return response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if not request.json:
        return jsonify({'error': 'No JSON data'}), 400
    
    try:
        response = requests.post(
            'http://whisper:8000/transcribe',
            json=request.json,
            timeout=30
        )
        return response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
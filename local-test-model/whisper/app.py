from flask import Flask, request, jsonify
import whisper
import torch
import os
from datetime import datetime
import logging

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load model
try:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Loading Whisper model on {device}")
    model = whisper.load_model("base", device=device)
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    raise

@app.route('/detect', methods=['POST'])
def detect():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file'}), 400
    
    try:
        audio_file = request.files['audio']
        filename = f"audio_{datetime.now().timestamp()}.wav"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio_file.save(filepath)
        
        # Process audio
        audio = whisper.load_audio(filepath)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        
        # Detect language
        _, probs = model.detect_language(mel)
        language = max(probs, key=probs.get)
        logger.info(f"Detected language: {language}")
        
        return jsonify({
            'status': 'success',
            'language': language,
            'filepath': filepath
        })
    except Exception as e:
        logger.error(f"Detection error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        data = request.json
        filepath = data.get('filepath')
        language = data.get('language')
        
        if not filepath or not os.path.exists(filepath):
            return jsonify({'error': 'Invalid file path'}), 400
        
        logger.info(f"Transcribing {filepath} in {language}")
        result = model.transcribe(filepath, language=language)
        os.remove(filepath)  # Clean up
        
        return jsonify({
            'status': 'success',
            'text': result['text']
        })
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
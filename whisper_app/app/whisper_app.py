from flask import Flask, request, jsonify
import whisper
import os

app = Flask(__name__)
UPLOAD_FOLDER = "/data/audio"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

model = whisper.load_model("tiny")

@app.route('/detect_language', methods=['POST'])
def detect_language():
    file = request.files['file']
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    audio = whisper.load_audio(path)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    _, probs = model.detect_language(mel)
    lang = max(probs, key=probs.get)
    return jsonify({"language": lang, "filename": file.filename})

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.get_json()
    filepath = os.path.join(UPLOAD_FOLDER, data['filename'])

    result = model.transcribe(filepath)
    return jsonify({"transcription": result["text"]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002)

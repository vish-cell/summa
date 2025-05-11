from flask import Flask, request, jsonify
import whisper
import torch
import os
from tempfile import NamedTemporaryFile
import uuid
import threading

app = Flask(__name__)

# Whisper setup
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("base", device=DEVICE)

# Job management
jobs = {}

@app.route('/get_audio', methods=['POST'])
def handle_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    job_id = str(uuid.uuid4())
    
    # Save to temp file
    temp_path = f"/tmp/{job_id}_{file.filename}"
    file.save(temp_path)
    
    # Language detection
    audio = whisper.load_audio(temp_path)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    _, probs = model.detect_language(mel)
    detected_lang = max(probs, key=probs.get)
    
    jobs[job_id] = {
        "file_path": temp_path,
        "language": detected_lang,
        "status": "language_detected",
        "confidence": float(probs[detected_lang])
    }
    
    return jsonify({
        "job_id": job_id,
        "language": detected_lang,
        "confidence": probs[detected_lang]
    })

@app.route('/status', methods=['POST'])
def handle_confirmation():
    data = request.get_json()
    job_id = data.get('job_id')
    confirm = data.get('confirm', False)
    
    if job_id not in jobs:
        return jsonify({"error": "Invalid job ID"}), 404
    
    if confirm:
        jobs[job_id]['status'] = "processing"
        
        # Start transcription in background
        threading.Thread(
            target=transcribe_audio,
            args=(job_id,)
        ).start()
        
        return jsonify({"status": "transcription_started"})
    else:
        jobs[job_id]['status'] = "cancelled"
        os.remove(jobs[job_id]['file_path'])
        return jsonify({"status": "cancelled"})

def transcribe_audio(job_id):
    try:
        job = jobs[job_id]
        result = model.transcribe(
            job['file_path'],
            language=job['language']
        )
        
        jobs[job_id].update({
            "status": "completed",
            "transcription": result["text"],
            "segments": result["segments"]
        })
        
        # Cleanup
        os.remove(job['file_path'])
        
    except Exception as e:
        jobs[job_id].update({
            "status": "error",
            "error": str(e)
        })

@app.route('/get_transcribe')
def get_transcription():
    job_id = request.args.get('job_id')
    if job_id not in jobs:
        return jsonify({"error": "Invalid job ID"}), 404
    
    job = jobs[job_id]
    response = {"status": job['status']}
    
    if job['status'] == "completed":
        response["transcription"] = job['transcription']
    elif job['status'] == "error":
        response["message"] = job['error']
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
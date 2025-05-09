from flask import Flask, render_template_string, send_file, redirect, url_for
import os

app = Flask(__name__)

DATA_DIR = "/data/audio"

@app.route("/")
def index():
    entries = []
    for file in os.listdir(DATA_DIR):
        if file.endswith(".mp3"):
            txt_file = file.replace(".mp3", ".txt")
            transcript = ""
            txt_path = os.path.join(DATA_DIR, txt_file)
            if os.path.exists(txt_path):
                with open(txt_path, "r") as f:
                    transcript = f.read()
            entries.append((file, transcript))
    return render_template_string(TEMPLATE, entries=entries)

@app.route("/download/<filename>")
def download(filename):
    return send_file(os.path.join(DATA_DIR, filename), as_attachment=True)

@app.route("/delete/<filename>")
def delete(filename):
    file_path = os.path.join(DATA_DIR, filename)
    txt_path = file_path.replace(".mp3", ".txt")
    if os.path.exists(file_path):
        os.remove(file_path)
    if os.path.exists(txt_path):
        os.remove(txt_path)
    return redirect(url_for("index"))

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Audio Visualizer</title>
    <style>
        body { font-family: Arial; padding: 20px; }
        .entry { border: 1px solid #ccc; margin-bottom: 15px; padding: 10px; }
        .audio-player { margin: 10px 0; }
        .transcript { white-space: pre-wrap; background: #f9f9f9; padding: 10px; }
        .actions { margin-top: 10px; }
    </style>
</head>
<body>
    <h1>Stored Audio Files</h1>
    {% for file, transcript in entries %}
    <div class="entry">
        <h3>{{ file }}</h3>
        <div class="audio-player">
            <audio controls>
                <source src="/download/{{ file }}" type="audio/mpeg">
                Your browser does not support the audio element.
            </audio>
        </div>
        <div class="transcript"><strong>Transcript:</strong><br>{{ transcript }}</div>
        <div class="actions">
            <a href="/download/{{ file }}">Download</a> |
            <a href="/delete/{{ file }}">Delete</a>
        </div>
    </div>
    {% else %}
        <p>No audio files found.</p>
    {% endfor %}
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7003)

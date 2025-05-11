// Service endpoints (resolved by Kubernetes DNS)
const WHISPER_SERVICE = "http://whisper-service:8000";
let currentJobId = null;

document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const transcribeBtn = document.getElementById('transcribeBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const newFileBtn = document.getElementById('newFileBtn');

    fileInput.addEventListener('change', handleFileSelect);
    uploadBtn.addEventListener('click', handleUpload);
    transcribeBtn.addEventListener('click', handleTranscription);
    cancelBtn.addEventListener('click', resetFlow);
    newFileBtn.addEventListener('click', resetFlow);
});

async function handleUpload() {
    const file = document.getElementById('fileInput').files[0];
    if (!file) return;

    showProgress('Uploading and detecting language...');
    
    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${WHISPER_SERVICE}/get_audio`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Language detection failed');

        const result = await response.json();
        currentJobId = result.job_id;

        document.getElementById('detectedLanguage').textContent = 
            `${result.language} (${Math.round(result.confidence * 100)}%)`;
        
        // Show audio preview
        const audioPreview = document.getElementById('audioPreview');
        audioPreview.src = URL.createObjectURL(file);
        audioPreview.style.display = 'block';

        // Show language confirmation
        document.getElementById('languageConfirm').style.display = 'block';
        document.getElementById('uploadBox').style.display = 'none';

    } catch (error) {
        showError(error.message);
    } finally {
        hideProgress();
    }
}

async function handleTranscription() {
    showProgress('Transcribing audio...');
    
    try {
        const response = await fetch(`${WHISPER_SERVICE}/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                job_id: currentJobId,
                confirm: true
            })
        });

        if (!response.ok) throw new Error('Transcription failed');

        // Poll for results
        const transcription = await pollTranscription();
        document.getElementById('transcriptionText').textContent = transcription;
        
        document.getElementById('languageConfirm').style.display = 'none';
        document.getElementById('resultsContainer').style.display = 'block';

    } catch (error) {
        showError(error.message);
    } finally {
        hideProgress();
    }
}

async function pollTranscription() {
    const maxAttempts = 10;
    const delay = 2000;
    
    for (let i = 0; i < maxAttempts; i++) {
        const response = await fetch(`${WHISPER_SERVICE}/get_transcribe?job_id=${currentJobId}`);
        if (response.ok) {
            const result = await response.json();
            if (result.status === 'completed') return result.transcription;
            if (result.status === 'error') throw new Error(result.message);
        }
        await new Promise(resolve => setTimeout(resolve, delay));
    }
    throw new Error('Transcription timed out');
}

function resetFlow() {
    document.getElementById('fileInput').value = '';
    document.getElementById('fileName').textContent = 'No file selected';
    document.getElementById('uploadBtn').disabled = true;
    document.getElementById('audioPreview').style.display = 'none';
    document.getElementById('languageConfirm').style.display = 'none';
    document.getElementById('resultsContainer').style.display = 'none';
    document.getElementById('uploadBox').style.display = 'block';
    document.getElementById('errorMessage').style.display = 'none';
    currentJobId = null;
}

function showProgress(message) {
    document.getElementById('progressText').textContent = message;
    document.getElementById('progressFill').style.width = '0%';
    document.getElementById('progressContainer').style.display = 'block';
    document.querySelectorAll('button').forEach(btn => btn.disabled = true);
    
    // Progress animation
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 10;
        document.getElementById('progressFill').style.width = `${Math.min(progress, 90)}%`;
        if (progress >= 90) clearInterval(interval);
    }, 300);
}

function hideProgress() {
    document.getElementById('progressFill').style.width = '100%';
    setTimeout(() => {
        document.getElementById('progressContainer').style.display = 'none';
        document.querySelectorAll('button').forEach(btn => btn.disabled = false);
    }, 500);
}

function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorMessage').style.display = 'block';
}
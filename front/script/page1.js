let mediaRecorder;
let audioChunks = [];

const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const status = document.getElementById("status");

startBtn.onclick = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  audioChunks = [];

  mediaRecorder.ondataavailable = event => {
    audioChunks.push(event.data);
  };

  mediaRecorder.onstop = () => {
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    const formData = new FormData();
    formData.append("file", audioBlob, "recorded.wav");

    fetch("http://whisper-service:8002/upload_audio", {
      method: "POST",
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      status.textContent = "Uploaded: " + data.file;
    })
    .catch(err => {
      status.textContent = "Upload failed.";
    });
  };

  mediaRecorder.start();
  status.textContent = "Recording...";
  startBtn.disabled = true;
  stopBtn.disabled = false;
};

stopBtn.onclick = () => {
  mediaRecorder.stop();
  status.textContent = "Stopping...";
  startBtn.disabled = false;
  stopBtn.disabled = true;
};

// Upload form
document.getElementById("uploadForm").onsubmit = (e) => {
  e.preventDefault();
  const fileInput = document.getElementById("audioFile");
  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  fetch("http://whisper-service:8002/upload_audio", {
    method: "POST",
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    status.textContent = "Uploaded: " + data.file;
  })
  .catch(err => {
    status.textContent = "Upload failed.";
  });
};

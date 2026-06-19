let stream = null;
let mediaRecorder = null;
let running = false;
let faceInterval = null;
let voiceInterval = null;

const video = document.getElementById("webcam");
const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");

let lastFace = {};
let lastVoice = { emotion: "detecting", confidence: 0 };

async function startCapture() {
  stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
  video.srcObject = stream;
  running = true;
  startBtn.disabled = true;
  stopBtn.disabled = false;

  await new Promise(resolve => {
    if (video.readyState >= 1) resolve();
    else video.onloadedmetadata = () => resolve();
  });

  faceInterval = setInterval(captureFace, 1000);
  voiceInterval = setInterval(captureVoice, 3000);
}

function stopCapture() {
  running = false;
  clearInterval(faceInterval);
  clearInterval(voiceInterval);
  if (mediaRecorder && mediaRecorder.state !== "inactive") mediaRecorder.stop();
  stream?.getTracks().forEach(t => t.stop());
  startBtn.disabled = false;
  stopBtn.disabled = true;
}

async function captureFace() {
  if (!running || !video.videoWidth) return;

  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video, 0, 0);
  const image = canvas.toDataURL("image/jpeg", 0.75);

  const res = await fetch("/api/analyze/face", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image }),
  });
  lastFace = await res.json();
  await postFusion();
}

async function captureVoice() {
  if (!running || !stream) return;

  const audioTrack = stream.getAudioTracks()[0];
  if (!audioTrack) return;

  const audioStream = new MediaStream([audioTrack]);
  mediaRecorder = new MediaRecorder(audioStream);
  const chunks = [];

  mediaRecorder.ondataavailable = e => chunks.push(e.data);
  mediaRecorder.onstop = async () => {
    const blob = new Blob(chunks, { type: "audio/webm" });
    const arrayBuffer = await blob.arrayBuffer();
    const audioCtx = new AudioContext({ sampleRate: 16000 });
    const decoded = await audioCtx.decodeAudioData(arrayBuffer);
    const samples = decoded.getChannelData(0);

    const res = await fetch("/api/analyze/voice", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ samples: Array.from(samples), sample_rate: 16000 }),
    });
    lastVoice = await res.json();
    await postFusion();
  };

  mediaRecorder.start();
  setTimeout(() => { if (mediaRecorder.state === "recording") mediaRecorder.stop(); }, 2500);
}

async function postFusion() {
  const res = await fetch("/api/analyze/fusion", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ face: lastFace, voice: lastVoice }),
  });
  const fused = await res.json();
  if (typeof updateDashboard === "function") updateDashboard(fused);
}

startBtn.addEventListener("click", startCapture);
stopBtn.addEventListener("click", stopCapture);

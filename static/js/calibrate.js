const STEPS = [
  { key: "neutral_face", text: "Sit neutral. Look at the camera.", type: "face" },
  { key: "happy_face", text: "Smile or look happy.", type: "face" },
  { key: "neutral_voice", text: "Speak normally.", type: "voice" },
];

const COUNTDOWN = 3;
const RECORD_SEC = 8;

let stepIdx = 0;
let samples = {};
let stream = null;
let running = false;

const calVideo = document.getElementById("calVideo");
const calInstruction = document.getElementById("calInstruction");
const calTimer = document.getElementById("calTimer");
const calProgress = document.getElementById("calProgress");
const calStatus = document.getElementById("calStatus");
const calStart = document.getElementById("calStart");
const calSkip = document.getElementById("calSkip");

calStart.addEventListener("click", startWizard);
calSkip.addEventListener("click", () => { location.href = "/"; });

async function startWizard() {
  stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
  calVideo.srcObject = stream;
  await new Promise(r => { calVideo.onloadedmetadata = r; });
  calStart.disabled = true;
  running = true;
  await runAllSteps();
}

async function runAllSteps() {
  for (stepIdx = 0; stepIdx < STEPS.length; stepIdx++) {
    if (!running) break;
    await runStep(STEPS[stepIdx]);
  }
  if (running) await finishCalibration();
}

async function runStep(step) {
  calInstruction.textContent = step.text;
  calStatus.textContent = "";

  for (let i = COUNTDOWN; i >= 1; i--) {
    calTimer.textContent = i;
    await sleep(1000);
  }

  calTimer.textContent = "go";
  await sleep(400);

  const captured = step.type === "face"
    ? await captureFaceSamples(RECORD_SEC)
    : await captureVoiceSample(RECORD_SEC);

  samples[step.key] = captured;
  calStatus.textContent = `${step.key}: ${captured.emotion} (${captured.confidence ? "ok" : "weak"})`;
}

async function captureFaceSamples(seconds) {
  const results = [];
  const end = Date.now() + seconds * 1000;
  while (Date.now() < end) {
    const pct = 1 - (end - Date.now()) / (seconds * 1000);
    calProgress.style.width = `${pct * 100}%`;

    const canvas = document.createElement("canvas");
    canvas.width = calVideo.videoWidth;
    canvas.height = calVideo.videoHeight;
    canvas.getContext("2d").drawImage(calVideo, 0, 0);
    const image = canvas.toDataURL("image/jpeg", 0.75);
    const res = await fetch("/api/analyze/face", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image }),
    });
    const data = await res.json();
    if (data.detected) results.push(data);
    await sleep(1000);
  }
  calProgress.style.width = "100%";
  return averageFace(results);
}

function averageFace(results) {
  if (!results.length) return { emotion: "neutral", confidence: 0, detected: false };
  const scores = {};
  results.forEach(r => {
    scores[r.emotion] = (scores[r.emotion] || 0) + r.confidence;
  });
  const top = Object.keys(scores).reduce((a, b) => scores[a] > scores[b] ? a : b);
  return {
    emotion: top,
    confidence: Math.round(scores[top] / results.length * 1000) / 1000,
    detected: true,
  };
}

async function captureVoiceSample(seconds) {
  const audioTrack = stream.getAudioTracks()[0];
  const audioStream = new MediaStream([audioTrack]);
  const recorder = new MediaRecorder(audioStream);
  const chunks = [];

  recorder.ondataavailable = e => chunks.push(e.data);
  const done = new Promise(resolve => { recorder.onstop = resolve; });
  recorder.start();

  const end = Date.now() + seconds * 1000;
  while (Date.now() < end) {
    calProgress.style.width = `${(1 - (end - Date.now()) / (seconds * 1000)) * 100}%`;
    await sleep(200);
  }
  recorder.stop();
  await done;

  const blob = new Blob(chunks, { type: "audio/webm" });
  const buf = await blob.arrayBuffer();
  const ctx = new AudioContext({ sampleRate: 16000 });
  const decoded = await ctx.decodeAudioData(buf);
  const samplesArr = decoded.getChannelData(0);

  const res = await fetch("/api/analyze/voice", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ samples: Array.from(samplesArr), sample_rate: 16000 }),
  });
  calProgress.style.width = "100%";
  return await res.json();
}

async function finishCalibration() {
  const res = await fetch("/api/calibrate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      step: "save",
      samples,
      created_at: new Date().toISOString(),
    }),
  });
  const data = await res.json();
  stream?.getTracks().forEach(t => t.stop());
  if (data.ok) {
    calInstruction.textContent = "Done.";
    calTimer.textContent = "✓";
    document.getElementById("calDoneControls").classList.remove("hidden");
    document.getElementById("calControls").classList.add("hidden");
  } else {
    calStatus.textContent = data.error || "save failed — try again";
    calStart.disabled = false;
  }
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

const STEPS = [
  { key: "neutral_face", text: "Sit neutral — look at the camera (8 sec)", duration: 8000 },
  { key: "happy_face", text: "Smile or look happy (8 sec)", duration: 8000 },
  { key: "neutral_voice", text: "Speak normally (8 sec)", duration: 8000 },
];

let stepIdx = 0;
let samples = {};
let stream = null;

const calVideo = document.getElementById("calVideo");
const calStep = document.getElementById("calStep");
const calStart = document.getElementById("calStart");
const calNext = document.getElementById("calNext");
const calStatus = document.getElementById("calStatus");

calStart.addEventListener("click", async () => {
  stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
  calVideo.srcObject = stream;
  calStart.disabled = true;
  calNext.disabled = false;
  runStep();
});

calNext.addEventListener("click", () => {
  stepIdx++;
  if (stepIdx >= STEPS.length) {
    finishCalibration();
  } else {
    runStep();
  }
});

async function runStep() {
  const step = STEPS[stepIdx];
  calStep.textContent = `Step ${stepIdx + 1}: ${step.text}`;
  calStatus.textContent = "Recording...";

  await new Promise(r => setTimeout(r, step.duration));

  if (step.key.includes("face")) {
    const canvas = document.createElement("canvas");
    canvas.width = calVideo.videoWidth;
    canvas.height = calVideo.videoHeight;
    canvas.getContext("2d").drawImage(calVideo, 0, 0);
    const image = canvas.toDataURL("image/jpeg", 0.7);
    const res = await fetch("/api/analyze/face", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image }),
    });
    samples[step.key] = await res.json();
  } else {
    samples[step.key] = { emotion: "neutral", confidence: 0.5 };
  }

  calStatus.textContent = `Captured ${step.key}`;
}

async function finishCalibration() {
  await fetch("/api/calibrate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      step: "save",
      samples,
      created_at: new Date().toISOString(),
    }),
  });
  stream?.getTracks().forEach(t => t.stop());
  calStatus.textContent = "Calibration saved. Head back to Live.";
  calNext.disabled = true;
}

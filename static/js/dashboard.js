const MOOD_COLORS = {
  angry: "#ef4444", happy: "#f59e0b", sad: "#3b82f6",
  neutral: "#71717a", fear: "#a855f7", surprise: "#22c55e",
  disgust: "#84cc16", unknown: "#52525b",
};

const MOOD_INDEX = { angry: 1, disgust: 2, fear: 3, happy: 4, sad: 5, surprise: 6, neutral: 7, unknown: 0 };

let timelineChart = null;
const timelineLabels = [];
const timelineData = [];

function initTimeline() {
  const ctx = document.getElementById("timelineChart").getContext("2d");
  timelineChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: timelineLabels,
      datasets: [{
        data: timelineData,
        borderColor: "#818cf8",
        tension: 0.35,
        pointRadius: 2,
        fill: false,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { display: false, min: 0, max: 8 },
        x: {
          ticks: { maxTicksLimit: 6, maxRotation: 0, color: "#71717a", font: { size: 10 } },
          grid: { display: false },
        },
      },
      plugins: { legend: { display: false } },
    },
  });
}

function setMoodColor(mood) {
  const base = (mood || "unknown").split("/")[0];
  const color = MOOD_COLORS[base] || MOOD_COLORS.unknown;
  document.documentElement.style.setProperty("--mood-color", color);
}

function setSignalRow(emotionEl, dotEl, strengthEl, emotion, strength) {
  const emo = emotion === "no_face" ? "—" : (emotion || "—");
  emotionEl.textContent = emo;
  strengthEl.textContent = strength || "offline";
  dotEl.className = "signal-dot " + (strength || "offline");
}

function setMoodLabel(mood, mismatch) {
  const el = document.getElementById("moodLabel");
  if (mismatch && mood.includes("/")) {
    const [face, voice] = mood.split("/");
    el.innerHTML = `<div class="mood-split"><span>${face.trim()}</span><span>${voice.trim()}</span></div>`;
  } else {
    const primary = mood.split("/")[0].trim();
    el.innerHTML = `<span class="mood-primary">${primary}</span>`;
  }
}

function updateDashboard(fused) {
  const mood = fused.mood || "unknown";
  setMoodLabel(mood, fused.mismatch);
  setMoodColor(mood.split("/")[0]);

  setSignalRow(
    document.getElementById("faceEmotion"),
    document.getElementById("faceDot"),
    document.getElementById("faceSignal"),
    fused.face_emotion,
    fused.face_signal,
  );
  setSignalRow(
    document.getElementById("voiceEmotion"),
    document.getElementById("voiceDot"),
    document.getElementById("voiceSignal"),
    fused.voice_emotion,
    fused.voice_signal,
  );

  const offline = document.getElementById("offlineBanner");
  if (fused.face_offline) offline.classList.remove("hidden");
  else offline.classList.add("hidden");

  const banner = document.getElementById("mismatchBanner");
  if (fused.mismatch) {
    banner.classList.remove("hidden");
    document.getElementById("mFace").textContent = fused.face_emotion;
    document.getElementById("mVoice").textContent = fused.voice_emotion;
  } else {
    banner.classList.add("hidden");
  }

  const base = mood.split("/")[0];
  const now = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  timelineLabels.push(now);
  timelineData.push(MOOD_INDEX[base] ?? 0);
  if (timelineLabels.length > 20) {
    timelineLabels.shift();
    timelineData.shift();
  }
  if (timelineChart) timelineChart.update();
}

async function pollDebug() {
  try {
    const res = await fetch("/api/debug/status");
    const d = await res.json();
    document.getElementById("debugText").textContent = JSON.stringify(d, null, 2);
  } catch (_) {}
}

async function checkCalibration() {
  const res = await fetch("/api/calibration/status");
  const data = await res.json();
  if (!data.calibrated && !localStorage.getItem("sentio_skip_cal")) {
    document.getElementById("calModal").classList.remove("hidden");
  }
}

document.getElementById("skipCal")?.addEventListener("click", () => {
  localStorage.setItem("sentio_skip_cal", "1");
  document.getElementById("calModal").classList.add("hidden");
});

document.addEventListener("DOMContentLoaded", () => {
  initTimeline();
  checkCalibration();
  setInterval(pollDebug, 5000);
});

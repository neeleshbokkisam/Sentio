const MOOD_COLORS = {
  angry: "#ef4444",
  disgust: "#84cc16",
  fear: "#a855f7",
  happy: "#f59e0b",
  sad: "#3b82f6",
  surprise: "#22c55e",
  neutral: "#6b7280",
  unknown: "#9ca3af",
};

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
        label: "Mood",
        data: timelineData,
        borderColor: "#6366f1",
        tension: 0.3,
        pointRadius: 3,
      }],
    },
    options: {
      responsive: true,
      scales: {
        y: { display: false },
        x: { ticks: { maxTicksLimit: 8, color: "#9ca3af" } },
      },
      plugins: { legend: { display: false } },
    },
  });
}

function setMoodColor(mood) {
  const base = mood.split("/")[0];
  const color = MOOD_COLORS[base] || MOOD_COLORS.unknown;
  document.documentElement.style.setProperty("--mood-color", color);
  return color;
}

function updateDashboard(fused) {
  const mood = fused.mood || "unknown";
  document.getElementById("moodLabel").textContent = mood;
  setMoodColor(mood);

  const avgConf = Math.round(((fused.face_confidence || 0) + (fused.voice_confidence || 0)) / 2 * 100);
  document.getElementById("moodConf").textContent = `confidence ${avgConf}%`;

  const facePct = Math.round((fused.face_confidence || 0) * 100);
  const voicePct = Math.round((fused.voice_confidence || 0) * 100);
  document.getElementById("faceBar").style.width = facePct + "%";
  document.getElementById("voiceBar").style.width = voicePct + "%";
  document.getElementById("facePct").textContent = facePct + "%";
  document.getElementById("voicePct").textContent = voicePct + "%";

  const banner = document.getElementById("mismatchBanner");
  if (fused.mismatch) {
    banner.classList.remove("hidden");
    document.getElementById("mFace").textContent = fused.face_emotion;
    document.getElementById("mVoice").textContent = fused.voice_emotion;
  } else {
    banner.classList.add("hidden");
  }

  const now = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  timelineLabels.push(now);
  timelineData.push(facePct); // numeric proxy for chart
  if (timelineLabels.length > 30) {
    timelineLabels.shift();
    timelineData.shift();
  }
  if (timelineChart) timelineChart.update();
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
});

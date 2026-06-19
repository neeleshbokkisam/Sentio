const MOOD_COLORS = {
  angry: "#ef4444", happy: "#f59e0b", sad: "#3b82f6",
  neutral: "#6b7280", fear: "#a855f7", surprise: "#22c55e",
};

let replayReadings = [];

async function loadInsights() {
  const [daily, weekly, sessions] = await Promise.all([
    fetch("/api/insights/daily").then(r => r.json()),
    fetch("/api/insights/weekly").then(r => r.json()),
    fetch("/api/sessions").then(r => r.json()),
  ]);

  renderDailyChart(daily);
  renderWeeklyChart(weekly);
  renderSessions(sessions);
}

function renderDailyChart(data) {
  const labels = Object.keys(data.counts || {});
  const values = Object.values(data.counts || {});
  const colors = labels.map(l => MOOD_COLORS[l.split("/")[0]] || "#6b7280");

  new Chart(document.getElementById("dailyChart"), {
    type: "doughnut",
    data: { labels, datasets: [{ data: values, backgroundColor: colors }] },
    options: { plugins: { legend: { labels: { color: "#e5e7eb" } } } },
  });
}

function renderWeeklyChart(data) {
  const days = (data.days || []).map(d => d.day);
  const counts = (data.days || []).map(d => d.count);

  new Chart(document.getElementById("weeklyChart"), {
    type: "bar",
    data: {
      labels: days,
      datasets: [{ label: "Readings", data: counts, backgroundColor: "#6366f1" }],
    },
    options: {
      scales: {
        x: { ticks: { color: "#9ca3af" } },
        y: { ticks: { color: "#9ca3af" } },
      },
      plugins: { legend: { display: false } },
    },
  });
}

function renderSessions(sessions) {
  const tbody = document.querySelector("#sessionsTable tbody");
  tbody.innerHTML = "";
  sessions.forEach(s => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${s.started_at?.slice(0, 19) || ""}</td>
      <td>${s.mode || ""}</td>
      <td>${s.reading_count || 0}</td>
      <td>${s.top_mood || "--"}</td>
      <td><button data-id="${s.id}" class="replay-btn">Replay</button>
          <a href="/api/export/${s.id}">CSV</a></td>`;
    tbody.appendChild(tr);
  });

  document.querySelectorAll(".replay-btn").forEach(btn => {
    btn.addEventListener("click", () => loadReplay(btn.dataset.id));
  });
}

async function loadReplay(sessionId) {
  const res = await fetch(`/api/sessions/${sessionId}/replay`);
  const data = await res.json();
  replayReadings = data.readings || [];

  const section = document.getElementById("replaySection");
  section.classList.remove("hidden");

  const slider = document.getElementById("replaySlider");
  slider.max = Math.max(0, replayReadings.length - 1);
  slider.value = 0;
  slider.oninput = () => showReplayFrame(parseInt(slider.value));
  showReplayFrame(0);
}

function showReplayFrame(idx) {
  const r = replayReadings[idx];
  if (!r) return;
  document.getElementById("replayDetail").innerHTML = `
    <p><strong>${r.timestamp}</strong></p>
    <p>Face: ${r.face} (${Math.round(r.face_conf * 100)}%)
       Voice: ${r.voice} (${Math.round(r.voice_conf * 100)}%)</p>
    <p>Mood: ${r.mood} ${r.mismatch ? '<span style="color:#f59e0b">MISMATCH</span>' : ""}</p>`;
}

document.addEventListener("DOMContentLoaded", loadInsights);
